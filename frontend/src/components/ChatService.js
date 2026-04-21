export async function sendQuestion(question) {
  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      throw new Error("Server error");
    }

    const data = await response.json();

    return data.answer || "No response";
  } catch (error) {
    return "⚠️ Cannot connect to AI server";
  }
}