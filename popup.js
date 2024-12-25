document.getElementById("ask-button").addEventListener("click", async () => {
    const input = document.getElementById("chat-input").value;

    const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
    });

    const data = await response.json();
    document.getElementById("response").innerText = data.answer || "Error processing request.";
});

document.getElementById("screenshot").addEventListener("click", async () => {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, async (dataUrl) => {
        const screenshotResponse = await fetch("http://127.0.0.1:5000/screenshot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ screenshot: dataUrl }),
        });

        const ocrData = await screenshotResponse.json();
        const instruction = document.getElementById("chat-input").value;

        const analysisResponse = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bounding_boxes: ocrData.bounding_boxes, instruction }),
        });

        const analysisData = await analysisResponse.json();
        console.log("Gemini Output:", analysisData.gemini_output || "Error analyzing data.");
    });
});
