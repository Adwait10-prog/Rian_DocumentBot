async function askQuestion() {
    const question = document.getElementById('question').value;
    const responseDiv = document.getElementById('response');
    const historyDiv = document.getElementById('history');

    const response = await fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question })
    });

    const data = await response.json();
    const answer = data.answer;

    responseDiv.innerHTML = `<p><strong>Answer:</strong> ${answer}</p>`;
    historyDiv.innerHTML += `<p><strong>Q:</strong> ${question}</p><p><strong>A:</strong> ${answer}</p>`;
}

async function uploadAudio() {
    const audioInput = document.getElementById('audio');
    const responseDiv = document.getElementById('response');
    const historyDiv = document.getElementById('history');

    const formData = new FormData();
    formData.append('audio', audioInput.files[0]);

    const response = await fetch('/speech-to-text', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    const recognizedText = data.text;

    responseDiv.innerHTML = `<p><strong>Recognized Text:</strong> ${recognizedText}</p>`;
    historyDiv.innerHTML += `<p><strong>Recognized Text:</strong> ${recognizedText}</p>`;
}
