// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "processScreenshot") {
      processScreenshot(request.screenshot);
    }
  });
  
  // Process screenshot with OCR
  async function processScreenshot(screenshot) {
    try {
      // Convert base64 to blob
      const response = await fetch(screenshot);
      const blob = await response.blob();
  
      // Create FormData
      const formData = new FormData();
      formData.append('image', blob);
  
      // Send to your Python backend
      const ocrResponse = await fetch('YOUR_BACKEND_URL/process-image', {
        method: 'POST',
        body: formData
      });
  
      const ocrData = await ocrResponse.json();
      
      // Process OCR results with Gemini
      const geminiResponse = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer AIzaSyANaYZ8rmgmGJrTIQYUTECoVvQYXc0Gbyo`
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: `Given these OCR results: ${JSON.stringify(ocrData)}, what is the next step the user should take? Please provide the exact coordinates of any UI elements they should interact with.`
            }]
          }]
        })
      });
  
      const geminiData = await geminiResponse.json();
      const nextStep = geminiData.candidates[0].content.parts[0].text;
  
      // Send coordinates to content script for highlighting
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: "highlight",
          coordinates: extractCoordinates(nextStep)
        });
      });
    } catch (error) {
      console.error('Processing error:', error);
    }
  }
  
  // Extract coordinates from Gemini response
  function extractCoordinates(response) {
    // This is a simple example - you'll need to adapt based on your actual response format
    const coords = response.match(/x=(\d+), y=(\d+), w=(\d+), h=(\d+)/);
    if (coords) {
      return {
        x: parseInt(coords[1]),
        y: parseInt(coords[2]),
        w: parseInt(coords[3]),
        h: parseInt(coords[4])
      };
    }
    return null;
  }