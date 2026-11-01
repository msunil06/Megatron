$(document).ready(function () {

    // Display Speak Message in Siri text and UI
    if (window.eel) {
        eel.expose(DisplayMessage);
        eel.expose(ShowHood);
        eel.expose(senderText);
        eel.expose(receiverText);
        eel.expose(showLiveResponse);
        eel.expose(hideLoader);
        eel.expose(hideFaceAuth);
        eel.expose(hideFaceAuthSuccess);
        eel.expose(hideStart);
    }

    function DisplayMessage(message) {
        if (!message) return;
        var targets = $(".siri-message");
        var listItems = targets.find(".texts li");

        if (listItems.length > 0) {
            listItems.text(message);
        } else {
            targets.text(message);
        }

        var statusLabel = $("#ListeningStatusLabel");
        if (statusLabel.length > 0) {
            statusLabel.text(message.toUpperCase());
        }

        try {
            targets.textillate('start');
        } catch (e) {
            targets.text(message);
        }
    }

    // Display Main Interactive Hood
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
        $("#AcousticListeningDock").fadeOut(250);
        if (window.refreshTrainingStats) {
            window.refreshTrainingStats();
        }
    }

    // Append user message to chat drawer
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (chatBox && message && message.trim() !== "") {
            chatBox.innerHTML += `
                <div class="row justify-content-end mb-3">
                    <div class="width-size">
                        <div class="sender_message">${escapeHtml(message)}</div>
                    </div>
                </div>
            `;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    // Append Megatron response to chat drawer
    function receiverText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (chatBox && message && message.trim() !== "") {
            chatBox.innerHTML += `
                <div class="row justify-content-start mb-3">
                    <div class="width-size">
                        <div class="receiver_message"><strong>Megatron:</strong> ${escapeHtml(message)}</div>
                    </div>
                </div>
            `;
            chatBox.scrollTop = chatBox.scrollHeight;
            if (window.refreshTrainingStats) {
                setTimeout(window.refreshTrainingStats, 600);
            }
        }
    }

    // Display Holographic Live Response directly on Main HUD screen
    function showLiveResponse(message) {
        if (!message) return;
        let box = $("#MegatronLiveResponseBox");
        let textEl = $("#MegatronLiveResponseText");
        if (box.length > 0 && textEl.length > 0) {
            textEl.html(escapeHtml(message).replace(/\n/g, '<br>'));
            box.fadeIn(250);
            try {
                box[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } catch (e) { }
        }
        // Browser Speech Synthesis for crisp, loud voice playback
        speakBrowserVoice(message);
        if (window.refreshTrainingStats) {
            setTimeout(window.refreshTrainingStats, 500);
        }
    }

    // Web Speech API Voice Player with graceful browser integration
    window.speakBrowserVoice = function(text) {
        if (!text || !('speechSynthesis' in window)) return;
        try {
            window.speechSynthesis.cancel(); // Cancel any prior utterances
            let clean = String(text)
                .replace(/[*_#`[\]()]/g, ' ')
                .replace(/\bhttps?:\/\/\S+/gi, ' ')
                .replace(/\s+/g, ' ')
                .trim();
            if (!clean) return;
            let utter = new SpeechSynthesisUtterance(clean);
            utter.rate = 1.05;
            utter.pitch = 1.0;
            let voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {
                let preferred = voices.find(v => v.lang && v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David') || v.name.includes('Zira') || v.name.includes('Guy')));
                if (preferred) utter.voice = preferred;
            }
            window.speechSynthesis.speak(utter);
        } catch (err) {
            console.log("[Browser Speech Synthesis Warning]", err);
        }
    };

    function escapeHtml(string) {
        return String(string)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // Biometric scanning state transitions
    function hideLoader() {
        $("#Loader").attr("hidden", true);
        $("#FaceAuth").attr("hidden", false);
    }

    function hideFaceAuth() {
        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);
    }

    function hideFaceAuthSuccess() {
        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", false);
    }

    // Hide Start Splash and display Main HUD
    function hideStart() {
        $("#Start").attr("hidden", true);
        setTimeout(function () {
            $("#Oval").attr("hidden", false);
            $("#Oval").addClass("animate__animated animate__zoomIn");
        }, 200);
    }

    // Safe global export
    window.MegatronController = {
        DisplayMessage: DisplayMessage,
        ShowHood: ShowHood,
        senderText: senderText,
        receiverText: receiverText,
        showLiveResponse: showLiveResponse,
        speakBrowserVoice: window.speakBrowserVoice
    };

});