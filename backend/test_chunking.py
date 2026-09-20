
from services.document_processor import clean_text, create_chunks


text = """
Layers of SPMR System Architecture

Ambient Assisted Living Layer

Collects physiological and contextual information from the patient using IoT devices and smart sensors.

Local Information Processing (LIP) Layer

Performs initial processing of collected data near the patient.

Cloud Management Module (CMM) Layer

Responsible for storing and managing current and historical patient information.

Cloud Analytics Management (CAM) Layer

Applies deep learning models for health condition prediction and generates personalized recommendations and alerts.
"""


text = clean_text(text)

chunks = create_chunks(text)

print("\n==============================")
print("        CHUNKING TEST")
print("==============================")

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):

    print(f"\n--- Chunk {index} ---")
    print(chunk)
    print("Characters:", len(chunk))

