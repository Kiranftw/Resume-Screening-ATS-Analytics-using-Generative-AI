import os
from ResumeAnalytics import ResumeAnalytics  # Replace with your module name
from typing import List

def get_pdf_paths() -> List[str]:
    print("Enter full path(s) to PDF document(s), separated by commas:")
    paths_input = input(">> ").strip()
    paths = [p.strip() for p in paths_input.split(",") if os.path.exists(p.strip())]
    if not paths:
        print("No valid files found.")
    return paths

def run_chatbot():
    print("📄 PDF Chatbot is starting...")
    pdf_paths = get_pdf_paths()

    if not pdf_paths:
        print("No valid documents provided. Exiting.")
        return

    chatbot = ResumeAnalytics()

    print("✅ Chatbot is ready! Ask questions based on the uploaded PDFs.")
    print("Type 'exit' or 'quit' to end the session.")

    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        response = chatbot.pdfchatbot(Documents=pdf_paths, Query=query)
        print(f"\n🤖 Bot:\n{response}")

if __name__ == "__main__":
    run_chatbot()