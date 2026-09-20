"use client";

import { useEffect, useState } from "react";

type SearchResult = {
  text: string;
  filename: string;
  page: number;
  section: string;
  rerank_score: number;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [documents, setDocuments] = useState<string[]>([]);
  const [selectedDocument, setSelectedDocument] = useState("");

  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatHistory, setChatHistory] = useState<
    Record<string, ChatMessage[]>
  >({});

  const loadDocuments = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/documents"
      );

      if (!response.ok) {
        throw new Error("Could not load documents");
      }

      const data = await response.json();

      setDocuments(data.documents || []);

      if (data.documents?.length > 0) {
        const firstDocument = data.documents[0];

        setSelectedDocument(firstDocument);

        setChatHistory((currentHistory) => {
          setMessages(currentHistory[firstDocument] || []);
          return currentHistory;
        });
      }
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const savedChatHistory = localStorage.getItem(
      "ai-document-chat-history"
    );

    if (savedChatHistory) {
      try {
        const parsedHistory = JSON.parse(savedChatHistory);

        setChatHistory(parsedHistory);

        const savedDocument = selectedDocument;

        if (savedDocument) {
          setMessages(parsedHistory[savedDocument] || []);
        }
      } catch (error) {
        console.error(
          "Failed to load saved chat history:",
          error
        );
      }
    }

    loadDocuments();
  }, []);

  useEffect(() => {
    if (Object.keys(chatHistory).length > 0) {
      localStorage.setItem(
        "ai-document-chat-history",
        JSON.stringify(chatHistory)
      );
    }
  }, [chatHistory]);

  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a PDF first.");
      return;
    }

    setLoading(true);
    setMessage("");
    setAnswer("");
    setResults([]);
    setMessages([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      if (data.duplicate) {
        setMessage(
          `${data.filename} is already in your document library.`
        );
      } else {
        setMessage(
          `${data.filename} uploaded successfully. ${data.total_chunks} searchable chunks created.`
        );
      }

      await loadDocuments();

      setSelectedDocument(data.filename);

      setMessages(
        chatHistory[data.filename] || []
      );
    } catch (error) {
      console.error(error);

      setMessage(
        "Unable to upload the PDF. Make sure the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!selectedDocument) {
      setAnswer("Please select a document first.");
      return;
    }

    if (!query.trim()) {
      setAnswer("Please enter a question.");
      return;
    }

    setSearching(true);
    setAnswer("");
    setResults([]);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/search?query=${encodeURIComponent(
          query
        )}&filename=${encodeURIComponent(selectedDocument)}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();

      const generatedAnswer =
        data.answer || "No answer was found.";

      setAnswer(generatedAnswer);
      setResults(data.results || []);

      const newMessages: ChatMessage[] = [
        ...messages,
        {
          role: "user",
          content: query,
        },
        {
          role: "assistant",
          content: generatedAnswer,
        },
      ];

      setMessages(newMessages);

      setChatHistory((previousHistory) => ({
        ...previousHistory,
        [selectedDocument]: newMessages,
      }));

      setQuery("");
    } catch (error) {
      console.error(error);

      setAnswer(
        "Something went wrong while searching. Make sure the backend server is running."
      );
    } finally {
      setSearching(false);
    }
  };

  const clearConversation = () => {
    setQuery("");
    setAnswer("");
    setResults([]);
    setMessages([]);

    if (selectedDocument) {
      setChatHistory((previousHistory) => ({
        ...previousHistory,
        [selectedDocument]: [],
      }));
    }
  };

  const deleteSelectedDocument = async () => {
    if (!selectedDocument) {
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/documents/${encodeURIComponent(
          selectedDocument
        )}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Delete failed");
      }

      const deletedDocument = selectedDocument;

      setAnswer("");
      setResults([]);
      setMessages([]);

      setChatHistory((previousHistory) => {
        const updatedHistory = {
          ...previousHistory,
        };

        delete updatedHistory[deletedDocument];

        return updatedHistory;
      });

      await loadDocuments();

      setMessage(
        `${deletedDocument} deleted successfully.`
      );

      setSelectedDocument("");
    } catch (error) {
      console.error(error);

      setMessage(
        "Unable to delete the selected document."
      );
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8 sm:px-6">
      <div className="mx-auto max-w-5xl">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-black text-xl text-white">
              AI
            </div>

            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                AI Document Assistant
              </h1>

              <p className="mt-1 text-sm text-slate-500">
                Ask questions and get answers grounded in your documents.
              </p>
            </div>

          </div>
        </div>

        {/* Main Card */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

          {/* Upload */}
          <section className="border-b border-slate-200 p-6 sm:p-8">

            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Step 1
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              Upload a document
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Upload a PDF to add it to your searchable document library.
            </p>

            <div className="mt-5 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-5">

              <input
                type="file"
                accept=".pdf"
                onChange={(event) => {
                  setFile(event.target.files?.[0] || null);
                  setMessage("");
                }}
                className="block w-full cursor-pointer text-sm text-slate-600 file:mr-4 file:rounded-lg file:border-0 file:bg-black file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-800"
              />

              {file && (
                <p className="mt-3 text-sm text-slate-600">
                  Selected:{" "}
                  <span className="font-medium text-slate-900">
                    {file.name}
                  </span>
                </p>
              )}

            </div>

            <button
              onClick={uploadFile}
              disabled={loading}
              className="mt-4 w-full rounded-xl bg-black px-5 py-3 font-medium text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Processing document..."
                : "Upload PDF"}
            </button>

            {message && (
              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                {message}
              </div>
            )}

          </section>

          {/* Document Selection + Questions */}
          <section className="p-6 sm:p-8">

            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Step 2
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              Ask about your document
            </h2>
            
            <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5">
              <span className="h-2 w-2 rounded-full bg-green-500" />

                <span className="text-xs font-medium text-slate-600">
                  {documents.length}{" "}
                  {documents.length === 1
                    ? "document"
                    : "documents"}{" "}
                  available
                </span>
            </div>

            <p className="mt-1 text-sm text-slate-500">
              Select a document and ask a question about its contents.
            </p>

            {/* Document Selector */}
            <div className="mt-5">

              <div className="mb-2 flex items-center justify-between">
                <label className="text-sm font-medium text-slate-700">
                  Select document
                </label>

                {selectedDocument && (
                  <span className="text-xs text-slate-400">
                    Active document
                  </span>
                )}
              </div>

              <select
                value={selectedDocument}
                onChange={(event) => {
                  const newDocument = event.target.value;

                  setSelectedDocument(newDocument);
                  setAnswer("");
                  setResults([]);
                  setQuery("");

                  setMessages(
                    chatHistory[newDocument] || []
                  );
                }}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              >
                {documents.length === 0 ? (
                  <option value="">
                    No documents uploaded
                  </option>
                ) : (
                  documents.map((document) => (
                    <option
                      key={document}
                      value={document}
                    >
                      {document}
                    </option>
                  ))
                )}
              </select>

              {selectedDocument && (
                <button
                  onClick={deleteSelectedDocument}
                  className="mt-3 rounded-xl border border-red-200 px-4 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50"
                >
                  Delete selected document
                </button>
              )}

            </div>

            {/* Question */}
            <div className="mt-5 flex flex-col gap-3 sm:flex-row">

              <input
                type="text"
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    askQuestion();
                  }
                }}
                placeholder="e.g. Explain the architecture of SPMR."
                className="flex-1 rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:bg-white focus:ring-2 focus:ring-slate-200 placeholder:text-slate-400"
              />

              <button
                onClick={askQuestion}
                disabled={searching || !selectedDocument}
                className="rounded-xl bg-black px-7 py-3 font-medium text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {searching ? "Searching..." : "Ask"}
              </button>

            </div>

            {/* Example Questions */}
            <div className="mt-4">

              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
                Try asking
              </p>

              <div className="flex flex-wrap gap-2">

                {[
                  "What is SPMR?",
                  "Explain the architecture of SPMR.",
                  "What are the limitations of existing systems?",
                  "How does SPMR work?",
                ].map((question) => (
                  <button
                    key={question}
                    onClick={() => setQuery(question)}
                    className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600 transition hover:border-slate-400 hover:bg-slate-50"
                  >
                    {question}
                  </button>
                ))}

              </div>

            </div>

            {/* Conversation */}
            {messages.length > 0 && (
              <div className="mt-8">

                <div className="flex items-center justify-between gap-4">

                  <h2 className="text-lg font-semibold text-slate-900">
                    Conversation
                  </h2>

                  <button
                    onClick={clearConversation}
                    className="text-sm text-slate-500 hover:text-slate-900"
                  >
                    Clear
                  </button>

                </div>

                <div className="mt-3 space-y-4">

                  {messages.map((message, index) => (

                    <div
                      key={index}
                      className={
                        message.role === "user"
                          ? "ml-auto max-w-3xl rounded-xl bg-black p-4 text-white shadow-sm"
                          : "max-w-3xl rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-800 shadow-sm"
                      }
                    >

                      <p className="mb-1 text-xs font-semibold uppercase tracking-wide opacity-60">
                        {message.role === "user"
                          ? "You"
                          : "AI Assistant"}
                      </p>

                      <p className="whitespace-pre-line text-sm leading-7">
                        {message.content}
                      </p>

                    </div>

                  ))}

                </div>

              </div>
            )}

            {/* Sources */}
            {results.length > 0 && (
              <div className="mt-8">

                <div className="flex items-center justify-between">

                  <h2 className="text-lg font-semibold text-slate-900">
                    Sources
                  </h2>

                  <span className="text-sm text-slate-500">
                    {results.length} relevant passages
                  </span>

                </div>

                <div className="mt-3 space-y-3">

                  {results.map((result, index) => (

                    <div
                      key={`${result.filename}-${result.page}-${index}`}
                      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
                    >

                      <div className="flex flex-wrap items-center gap-2">

                        <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-medium text-white">
                          Source {index + 1}
                        </span>

                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                          Page {result.page}
                        </span>

                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                          {result.section}
                        </span>

                      </div>

                      <p className="mt-3 text-xs font-medium text-slate-400">
                        {result.filename}
                      </p>

                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        {result.text}
                      </p>

                    </div>

                  ))}

                </div>

              </div>
            )}

          </section>

        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          Local RAG pipeline • Semantic retrieval • Cross-encoder reranking
        </p>

      </div>
    </main>
  );
}