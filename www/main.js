$(document).ready(function () {

    // Immediately open directly into Megatron Agent HUD (no face recognition required)
    $("#Start").attr("hidden", true);
    $("#Oval").attr("hidden", false);
    eel.init()();

    // Query execution mode ('browser', 'windows_app', 'android_app')
    try {
        eel.getAppMode()(function (mode) {
            if (mode === "windows_app") {
                $("#HudModePill").html('<i class="bi bi-windows text-info"></i> WINDOWS SUITE (FULL PC CONTROL)');
                $(".app-only-feature").show();
                $("#HudSystemControlBtn").show();
            } else if (mode === "android_app") {
                $("#HudModePill").html('<i class="bi bi-android2 text-success"></i> ANDROID APP (FULL DEVICE CONTROL)');
                $(".app-only-feature").show();
                $("#HudSystemControlBtn").show();
            } else {
                $("#HudModePill").html('<span class="pulse-dot"></span> WEB AGENT MODE (DATA ACCESS)');
                $(".app-only-feature").hide();
                $("#HudSystemControlBtn").hide();
                $("#HudAdminStatusPill").hide();
                $("#QuickMemoryBtn").hide();
                $("#MemoryBtn").hide();
            }
        });
    } catch (e) {
        console.log("getAppMode error:", e);
    }

    // Android Mobile Native Bridge Detection
    if (window.MegatronMobileBridge) {
        $("#HudModePill").html('<i class="bi bi-android2 text-success"></i> ANDROID APP (FULL DEVICE CONTROL)');
    }

    // Register Service Worker for Android PWA Installation
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js').catch(function (err) {
            console.log('SW register:', err);
        });
    }

    // Skip biometric scan button fallback
    $("#SkipAuthBtn").click(function () {
        eel.skipAuth()();
    });

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },
    });

    // Siri Wave configuration (Megatron Cyan)
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios",
        color: "#00f0ff",
        amplitude: "1.2",
        speed: "0.25",
        autostart: true
    });

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },
    });

    // Mic button click & Arc Reactor click (Inline Acoustic Telemetry)
    var voiceListeningTimeout = null;

    function startVoiceListening() {
        try {
            eel.playAssistantSound();
        } catch (e) { }

        // Keep Main HUD visible, activate inline acoustic dock
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
        $("#AcousticListeningDock").fadeIn(200);
        $("#ListeningStatusLabel").text("LISTENING FOR VOICE COMMAND...");

        // 10-second fail-safe timeout so UI never remains stuck
        if (voiceListeningTimeout) clearTimeout(voiceListeningTimeout);
        voiceListeningTimeout = setTimeout(function () {
            $("#AcousticListeningDock").fadeOut(250);
        }, 10000);

        try {
            eel.allCommands()();
        } catch (e) {
            console.log("allCommands voice error:", e);
            $("#AcousticListeningDock").fadeOut(250);
        }
    }

    $("#MicBtn").click(startVoiceListening);
    $("#MegatronCoreHub").click(startVoiceListening);

    $("#CancelVoiceListeningBtn").click(function () {
        if (voiceListeningTimeout) clearTimeout(voiceListeningTimeout);
        $("#AcousticListeningDock").fadeOut(200);
    });

    $("#BackToHudBtn").click(function () {
        $("#SiriWave").attr("hidden", true);
        $("#Oval").attr("hidden", false);
    });

    // Keyboard shortcut handler (Win+J or Ctrl+J or Ctrl+Space)
    function doc_keyUp(e) {
        if ((e.key === 'j' && (e.metaKey || e.ctrlKey)) || (e.code === 'Space' && e.ctrlKey)) {
            startVoiceListening();
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // Send query to assistant without hiding HUD
    function PlayAssistant(message) {
        if (!message || message.trim() === "") return;
        let query = message.trim();

        // 1. Keep Main HUD 100% visible and interactive
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
        $("#AcousticListeningDock").fadeOut(150);

        // 2. Immediately show Holographic Live Response Box in thinking state
        let box = $("#MegatronLiveResponseBox");
        let textEl = $("#MegatronLiveResponseText");
        textEl.html(`
            <div class="d-flex align-items-center gap-2 py-2 text-info">
                <span class="spinner-border spinner-border-sm text-info" role="status"></span>
                <span style="letter-spacing: 1px;">Megatron Neural Core is analyzing: <em>"${escapeHtml(query)}"</em>...</span>
            </div>
        `);
        box.fadeIn(200);

        // 3. Append to chat history drawer
        var chatBox = document.getElementById("chat-canvas-body");
        if (chatBox) {
            chatBox.innerHTML += `
                <div class="row justify-content-end mb-3">
                    <div class="width-size">
                        <div class="sender_message">${escapeHtml(query)}</div>
                    </div>
                </div>
            `;
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // 4. Send to backend Eel router
        try {
            eel.allCommands(query)();
        } catch (e) {
            console.log("allCommands call error:", e);
        }

        // 5. Reset input field
        $("#chatbox").val("");
        ShowHideButton("");

        setTimeout(function () {
            if (window.refreshTrainingStats) window.refreshTrainingStats();
        }, 2000);
    }

    // Toggle button visibility based on chat input
    function ShowHideButton(message) {
        if (!message || message.length === 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        } else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    $("#chatbox").keyup(function () {
        let message = $("#chatbox").val();
        ShowHideButton(message);
    });

    $("#SendBtn").click(function () {
        let message = $("#chatbox").val();
        PlayAssistant(message);
    });

    $("#chatbox").keypress(function (e) {
        if (e.which === 13) {
            let message = $("#chatbox").val();
            PlayAssistant(message);
        }
    });

    // Online AI quick launcher buttons
    $(".ai-quick-btn[data-ai]").click(function () {
        let ai = $(this).attr("data-ai");
        let prompt = $("#chatbox").val().trim();
        eel.openOnlineAI(ai, prompt)();
        if (prompt.length > 0) {
            $("#chatbox").val("");
            ShowHideButton("");
        }
    });

    // Live Weather quick button
    $("#QuickWeatherBtn").click(function () {
        let city = $("#chatbox").val().trim();
        PlayAssistant(city ? "weather in " + city : "what is the current weather");
    });

    // Live News quick button
    $("#QuickNewsBtn").click(function () {
        let topic = $("#chatbox").val().trim();
        PlayAssistant(topic ? "news about " + topic : "top news headlines");
    });

    // Quick suggestion chips in chat drawer
    $(document).on("click", ".quick-chip", function () {
        let cmd = $(this).attr("data-cmd");
        PlayAssistant(cmd);
    });

    // --- Load Stored Settings & Database Data ---
    eel.personalInfo()();
    eel.displaySysCommand()();
    eel.displayWebCommand()();
    eel.displayPhoneBookCommand()();

    // Load Gemini API Key
    try {
        eel.getApiKey()(function (key) {
            if (key) {
                $("#InputGeminiKey").val(key);
            }
        });
    } catch (e) {
        console.log("getApiKey error:", e);
    }

    // Toggle API Key visibility
    $("#ToggleKeyVisibility").click(function () {
        let field = $("#InputGeminiKey");
        let currentType = field.attr("type");
        if (currentType === "password") {
            field.attr("type", "text");
            $(this).html('<i class="bi bi-eye-slash"></i>');
        } else {
            field.attr("type", "password");
            $(this).html('<i class="bi bi-eye"></i>');
        }
    });

    // Save API Key button
    $("#SaveApiKeyBtn").click(function () {
        let key = $("#InputGeminiKey").val().trim();
        eel.updateApiKey(key)(function (res) {
            if (res === 1) {
                swal({
                    title: "Megatron Settings Saved",
                    text: "AI intelligence credentials updated successfully.",
                    icon: "success",
                });
            } else {
                swal({
                    title: "Error",
                    text: "Could not save AI settings.",
                    icon: "error",
                });
            }
        });
    });

    // Populate user profile info
    eel.expose(getData);
    function getData(user_info) {
        let data = JSON.parse(user_info);
        let idsPersonalInfo = ['OwnerName', 'Designation', 'MobileNo', 'Email', 'City'];
        let idsInputInfo = ['InputOwnerName', 'InputDesignation', 'InputMobileNo', 'InputEmail', 'InputCity'];

        for (let i = 0; i < data.length; i++) {
            let hashid = "#" + idsPersonalInfo[i];
            $(hashid).text(data[i]);
            $("#" + idsInputInfo[i]).val(data[i]);
        }
    }

    // Update Personal Profile
    $("#UpdateBtn").click(function () {
        let OwnerName = $("#InputOwnerName").val().trim();
        let Designation = $("#InputDesignation").val().trim();
        let MobileNo = $("#InputMobileNo").val().trim();
        let Email = $("#InputEmail").val().trim();
        let City = $("#InputCity").val().trim();

        if (OwnerName.length > 0 && Designation.length > 0 && MobileNo.length > 0) {
            eel.updatePersonalInfo(OwnerName, Designation, MobileNo, Email, City);
            swal({
                title: "Profile Updated",
                text: "Your profile information has been saved.",
                icon: "success",
            });
        } else {
            const toastLiveExample = document.getElementById('liveToast');
            const toast = new bootstrap.Toast(toastLiveExample);
            $("#ToastMessage").text("Name, Designation and Mobile No are mandatory.");
            toast.show();
        }
    });

    // Display System Commands in Table
    eel.expose(displaySysCommand);
    function displaySysCommand(array) {
        let data = JSON.parse(array);
        let placeholder = document.querySelector("#TableData");
        let out = "";
        for (let i = 0; i < data.length; i++) {
            out += `
                <tr>
                    <td class="text-light">${i + 1}</td>
                    <td class="text-light">${data[i][1]}</td>
                    <td class="text-light" style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${data[i][2]}</td>
                    <td class="text-light"><button id="${data[i][0]}" onClick="SysDeleteID(this.id)" class="btn btn-sm btn-glow-red">Delete</button></td>
                </tr>
            `;
        }
        placeholder.innerHTML = out;
    }

    // Add System Command
    $("#SysCommandAddBtn").click(function () {
        let key = $("#SysCommandKey").val().trim();
        let value = $("#SysCommandValue").val().trim();

        if (key.length > 0 && value.length > 0) {
            eel.addSysCommand(key, value);
            swal({
                title: "System Command Added",
                icon: "success",
            });
            setTimeout(function () {
                eel.displaySysCommand()();
            }, 300);
            $("#SysCommandKey").val("");
            $("#SysCommandValue").val("");
        } else {
            const toastLiveExample = document.getElementById('liveToast');
            const toast = new bootstrap.Toast(toastLiveExample);
            $("#ToastMessage").text("Both keyword and path are required.");
            toast.show();
        }
    });

    // Display Web Commands in Table
    eel.expose(displayWebCommand);
    function displayWebCommand(array) {
        let data = JSON.parse(array);
        let placeholder = document.querySelector("#WebTableData");
        let out = "";
        for (let i = 0; i < data.length; i++) {
            out += `
                <tr>
                    <td class="text-light">${i + 1}</td>
                    <td class="text-light">${data[i][1]}</td>
                    <td class="text-light" style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${data[i][2]}</td>
                    <td class="text-light"><button id="${data[i][0]}" onClick="WebDeleteID(this.id)" class="btn btn-sm btn-glow-red">Delete</button></td>
                </tr>
            `;
        }
        placeholder.innerHTML = out;
    }

    // Add Web Command
    $("#WebCommandAddBtn").click(function () {
        let key = $("#WebCommandKey").val().trim();
        let value = $("#WebCommandValue").val().trim();

        if (key.length > 0 && value.length > 0) {
            eel.addWebCommand(key, value);
            swal({
                title: "Web Command Added",
                icon: "success",
            });
            setTimeout(function () {
                eel.displayWebCommand()();
            }, 300);
            $("#WebCommandKey").val("");
            $("#WebCommandValue").val("");
        } else {
            const toastLiveExample = document.getElementById('liveToast');
            const toast = new bootstrap.Toast(toastLiveExample);
            $("#ToastMessage").text("Both keyword and URL are required.");
            toast.show();
        }
    });

    // Display Phone Book in Table
    eel.expose(displayPhoneBookCommand);
    function displayPhoneBookCommand(array) {
        let data = JSON.parse(array);
        let placeholder = document.querySelector("#ContactTableData");
        let out = "";
        for (let i = 0; i < data.length; i++) {
            out += `
                <tr>
                    <td class="text-light">${i + 1}</td>
                    <td class="text-light">${data[i][1]}</td>
                    <td class="text-light">${data[i][2]}</td>
                    <td class="text-light">${data[i][3] || '-'}</td>
                    <td class="text-light">${data[i][4] || '-'}</td>
                    <td class="text-light"><button id="${data[i][0]}" onClick="ContactDeleteID(this.id)" class="btn btn-sm btn-glow-red">Delete</button></td>
                </tr>
            `;
        }
        placeholder.innerHTML = out;
    }

    // Add Contact
    $("#AddContactBtn").click(function () {
        let Name = $("#InputContactName").val().trim();
        let MobileNo = $("#InputContactMobileNo").val().trim();
        let Email = $("#InputContactEmail").val().trim();
        let City = $("#InputContactCity").val().trim();

        if (Name.length > 0 && MobileNo.length > 0) {
            eel.InsertContacts(Name, MobileNo, Email || "", City || "");
            swal({
                title: "Contact Saved",
                text: `${Name} has been added to your phone book.`,
                icon: "success",
            });
            $("#InputContactName").val("");
            $("#InputContactMobileNo").val("");
            $("#InputContactEmail").val("");
            $("#InputContactCity").val("");
            setTimeout(function () {
                eel.displayPhoneBookCommand()();
            }, 300);
        } else {
            const toastLiveExample = document.getElementById('liveToast');
            const toast = new bootstrap.Toast(toastLiveExample);
            $("#ToastMessage").text("Name and Mobile Number are required.");
            toast.show();
        }
    });

    // ========================================================
    // VISUAL SOLUTION FINDER & IMAGE UPLOAD
    // ========================================================
    let currentUploadedBase64 = "";
    let currentUploadedFileName = "";
    let currentEngineChoice = "megatron_ai";

    // Open Image Modal
    $("#ImageSearchBtn, #QuickImageSearchBtn").click(function () {
        var imageModal = new bootstrap.Modal(document.getElementById('ImageSearchModal'));
        imageModal.show();
    });

    // Open Search Memory Tab
    $("#MemoryBtn, #QuickMemoryBtn").click(function () {
        var settingsModal = new bootstrap.Modal(document.getElementById('exampleModal'));
        settingsModal.show();
        var memoryTabBtn = document.querySelector('#nav-memory-tab');
        if (memoryTabBtn) {
            var tab = new bootstrap.Tab(memoryTabBtn);
            tab.show();
        }
        loadSearchMemory();
    });

    // Engine selector cards
    $(document).on("click", ".engine-card", function () {
        $(".engine-card").removeClass("active");
        $(this).addClass("active");
        currentEngineChoice = $(this).attr("data-engine");
    });

    // Browse Image click
    $("#BrowseImageLink").click(function (e) {
        e.stopPropagation();
        $("#ImageFileInput").click();
    });

    $("#DropZonePrompt").click(function () {
        $("#ImageFileInput").click();
    });

    // File input change
    $("#ImageFileInput").change(function () {
        if (this.files && this.files[0]) {
            handleImageFile(this.files[0]);
        }
    });

    // Drag & Drop handlers
    let dropZone = document.getElementById("ImageDropZone");
    if (dropZone) {
        dropZone.addEventListener("dragover", function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).addClass("dragover");
        });
        dropZone.addEventListener("dragleave", function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).removeClass("dragover");
        });
        dropZone.addEventListener("drop", function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).removeClass("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleImageFile(e.dataTransfer.files[0]);
            }
        });
    }

    // Global Clipboard Paste Handler (Ctrl+V)
    window.addEventListener("paste", function (e) {
        if (e.clipboardData && e.clipboardData.items) {
            for (let i = 0; i < e.clipboardData.items.length; i++) {
                let item = e.clipboardData.items[i];
                if (item.type.indexOf("image") !== -1) {
                    let blob = item.getAsFile();
                    handleImageFile(blob);
                    var imageModal = new bootstrap.Modal(document.getElementById('ImageSearchModal'));
                    imageModal.show();
                    break;
                }
            }
        }
    });

    function handleImageFile(file) {
        if (!file || !file.type.match(/image.*/)) {
            swal("Invalid File", "Please select or drop an image file (PNG, JPG, WEBP).", "warning");
            return;
        }
        currentUploadedFileName = file.name || "pasted_image.png";
        let reader = new FileReader();
        reader.onload = function (e) {
            currentUploadedBase64 = e.target.result;
            $("#ImagePreview").attr("src", currentUploadedBase64);
            let sizeKb = Math.round(file.size / 1024);
            $("#ImageFileInfo").text(`${currentUploadedFileName} (${sizeKb} KB)`);
            $("#DropZonePrompt").hide();
            $("#ImagePreviewContainer").fadeIn(200);
            $("#ImageSolutionResultBox").hide();
        };
        reader.readAsDataURL(file);
    }

    // Remove image button
    $("#RemoveImageBtn").click(function () {
        currentUploadedBase64 = "";
        currentUploadedFileName = "";
        $("#ImageFileInput").val("");
        $("#ImagePreview").attr("src", "");
        $("#ImagePreviewContainer").hide();
        $("#DropZonePrompt").fadeIn(200);
        $("#ImageSolutionResultBox").hide();
    });

    // Submit Visual Solution Search
    $("#SubmitImageSearchBtn").click(function () {
        if (!currentUploadedBase64) {
            swal("No Image Selected", "Please drag, drop, paste, or browse an image first.", "warning");
            return;
        }
        let prompt = $("#ImageSearchPrompt").val().trim();
        let btn = $(this);
        btn.prop("disabled", true);
        $("#SubmitBtnSpinner").show();
        $("#SubmitBtnIcon").hide();

        eel.uploadImageSearch(currentUploadedBase64, currentUploadedFileName, currentEngineChoice, prompt)(function (res) {
            btn.prop("disabled", false);
            $("#SubmitBtnSpinner").hide();
            $("#SubmitBtnIcon").show();

            if (res && res.solution) {
                $("#ImageSolutionText").text(res.solution);
                $("#ImageSolutionResultBox").fadeIn(300);
                swal("Solution Found", "Megatron Vision AI has analyzed the image and generated the complete solution.", "success");
            } else if (res && res.message) {
                swal(res.engine || "Visual Search", res.message, "info");
            }
            loadSearchMemory();
        });
    });

    // Copy Solution Button
    $("#CopySolutionBtn").click(function () {
        let text = $("#ImageSolutionText").text();
        if (text && navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function () {
                swal("Copied!", "Solution copied to clipboard.", "success");
            });
        }
    });

    // ========================================================
    // MEGATRON AI // MAIN ADMIN NEURAL VAULT GATE
    // Trained Data & Memory are strictly restricted to Main Admin
    // ========================================================
    let currentAdminPasscode = sessionStorage.getItem("megatron_admin_passcode") || "";

    function updateAdminVaultUI() {
        if (currentAdminPasscode) {
            $("#AdminLockedVaultView").hide();
            $("#AdminUnlockedVaultView").fadeIn(250);
            $("#HudAdminStatusPill")
                .removeClass("hud-pill-admin-locked")
                .addClass("hud-pill-admin-active")
                .html('<i class="bi bi-shield-fill-check"></i> ADMIN: LEVEL 0');
            loadSearchMemory();
        } else {
            $("#AdminUnlockedVaultView").hide();
            $("#AdminLockedVaultView").fadeIn(250);
            $("#HudAdminStatusPill")
                .removeClass("hud-pill-admin-active")
                .addClass("hud-pill-admin-locked")
                .html('<i class="bi bi-shield-lock-fill"></i> ADMIN: LOCKED');
            let tbody = document.getElementById("MemoryTableBody");
            if (tbody) tbody.innerHTML = "";
            $("#StatSearchesCount").text("0");
            $("#StatTopicsCount").text("0");
        }
    }

    // Toggle passcode input visibility
    $("#ToggleAdminPasscodeVisibility").click(function () {
        let field = $("#AdminPasscodeInput");
        let type = field.attr("type") === "password" ? "text" : "password";
        field.attr("type", type);
        $(this).find("i").toggleClass("bi-eye bi-eye-slash");
    });

    // Authenticate Admin Clearance
    $("#AdminAuthSubmitBtn").click(function () {
        let pin = $("#AdminPasscodeInput").val().trim();
        if (!pin) {
            $("#AdminAuthAlert").text("Please enter the Main Admin Master Passcode.").fadeIn(200);
            return;
        }
        let btn = $(this);
        btn.prop("disabled", true);
        $("#AdminAuthSpinner").show();
        $("#AdminAuthAlert").hide();

        eel.verifyAdminAccess(pin)(function (resStr) {
            btn.prop("disabled", false);
            $("#AdminAuthSpinner").hide();

            let res = typeof resStr === "string" ? JSON.parse(resStr) : resStr;
            if (res && res.success) {
                currentAdminPasscode = pin;
                sessionStorage.setItem("megatron_admin_passcode", pin);
                $("#AdminPasscodeInput").val("");
                $("#AdminAuthAlert").hide();
                updateAdminVaultUI();
                swal("Clearance Granted", "Welcome, Main Administrator. Megatron Neural Vault unlocked.", "success");
            } else {
                $("#AdminAuthAlert").text(res && res.message ? res.message : "Access Denied: Invalid Master Passcode.").fadeIn(200);
                swal("Access Denied", "Invalid Master Passcode. Trained neural data is restricted.", "error");
            }
        });
    });

    // Enter key trigger for admin password
    $("#AdminPasscodeInput").on("keypress", function (e) {
        if (e.which === 13) {
            $("#AdminAuthSubmitBtn").click();
        }
    });

    // Change Admin Master Passcode
    $("#SubmitChangePasscodeBtn").click(function () {
        let curr = $("#CurrentAdminPasscodeInput").val().trim();
        let newPin = $("#NewAdminPasscodeInput").val().trim();
        let feedback = $("#ChangePasscodeFeedback");

        if (!curr || !newPin) {
            feedback.text("Please fill both current and new passcode.").css("color", "#ef4444");
            return;
        }
        if (newPin.length < 4) {
            feedback.text("New passcode must be at least 4 characters long.").css("color", "#ef4444");
            return;
        }

        eel.changeAdminPasscode(curr, newPin)(function (resStr) {
            let res = typeof resStr === "string" ? JSON.parse(resStr) : resStr;
            if (res && res.success) {
                currentAdminPasscode = newPin;
                sessionStorage.setItem("megatron_admin_passcode", newPin);
                $("#CurrentAdminPasscodeInput").val("");
                $("#NewAdminPasscodeInput").val("");
                feedback.text(res.message).css("color", "#22c55e");
                let collapseEl = document.getElementById('ChangePasscodeBox');
                let bsCollapse = bootstrap.Collapse.getInstance(collapseEl);
                if (bsCollapse) bsCollapse.hide();
                swal("Passcode Updated", "Admin Master Passcode successfully updated.", "success");
            } else {
                feedback.text(res && res.message ? res.message : "Error changing passcode.").css("color", "#ef4444");
            }
        });
    });

    // Revoke Admin Session / Lock Vault
    $("#AdminLockoutBtn").click(function () {
        currentAdminPasscode = "";
        sessionStorage.removeItem("megatron_admin_passcode");
        updateAdminVaultUI();
        swal("Vault Secured", "Trained neural data locked. Clearance revoked.", "info");
    });

    // System Controls button routing (Active only in Windows / Android app)
    $("#HudSystemControlBtn").click(function () {
        let modalEl = document.getElementById('exampleModal');
        let modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
        let triggerEl = document.querySelector('#nav-profile-tab');
        if (triggerEl) {
            bootstrap.Tab.getOrCreateInstance(triggerEl).show();
        }
    });

    // Load Search Memory (STRICTLY REQUIRES ADMIN PASSCODE)
    function loadSearchMemory() {
        if (!currentAdminPasscode) {
            return;
        }
        try {
            eel.getMemoryStats(currentAdminPasscode)(function (statsJson) {
                let stats = typeof statsJson === "string" ? JSON.parse(statsJson) : statsJson;
                if (stats && !stats.locked) {
                    $("#StatSearchesCount").text(stats.searches || 0);
                    $("#StatTopicsCount").text(stats.topics || 0);
                }
            });

            eel.getSearchHistory(100, currentAdminPasscode)(function (historyJson) {
                let data = typeof historyJson === "string" ? JSON.parse(historyJson) : historyJson;
                if (data && data.error === "ACCESS_DENIED") {
                    currentAdminPasscode = "";
                    sessionStorage.removeItem("megatron_admin_passcode");
                    updateAdminVaultUI();
                    return;
                }
                renderMemoryTable(data);
            });
        } catch (err) {
            console.log("Memory load error:", err);
        }
    }

    function renderMemoryTable(data) {
        let tbody = document.getElementById("MemoryTableBody");
        if (!tbody) return;

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted p-4">No search records in vault. Use Megatron to search online or solve questions to build trained intelligence!</td></tr>`;
            return;
        }

        let out = "";
        for (let i = 0; i < data.length; i++) {
            let id = data[i][0];
            let query = escapeStr(data[i][1] || "");
            let response = escapeStr(data[i][2] || "-");
            let category = (data[i][3] || "general").toLowerCase();
            let time = data[i][4] || "";

            let badgeClass = "bg-secondary";
            let badgeText = category;
            if (category === "ai_chat") { badgeClass = "bg-info text-dark"; badgeText = "AI Chat"; }
            else if (category === "web_search") { badgeClass = "bg-warning text-dark"; badgeText = "Web Search"; }
            else if (category === "image_ai" || category === "image_search") { badgeClass = "bg-info text-dark"; badgeText = "Visual Solution"; }
            else if (category === "weather") { badgeClass = "bg-info text-dark"; badgeText = "Weather"; }
            else if (category === "news") { badgeClass = "bg-primary text-light"; badgeText = "News"; }
            else if (category === "media") { badgeClass = "bg-dark border border-info text-info"; badgeText = "Media"; }

            out += `
                <tr data-search-id="${id}" class="memory-row">
                    <td class="text-muted small">${i + 1}</td>
                    <td class="text-muted small">${time}</td>
                    <td><span class="badge ${badgeClass} category-badge">${badgeText}</span></td>
                    <td class="text-light fw-bold query-cell" style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${query}">${query}</td>
                    <td class="text-muted response-cell" style="max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${response}">${response}</td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-info me-1 run-memory-btn" data-query="${query}" title="Execute query again"><i class="bi bi-play-fill"></i></button>
                        <button class="btn btn-sm btn-outline-secondary delete-memory-btn" data-id="${id}" title="Purge record"><i class="bi bi-trash"></i></button>
                    </td>
                </tr>
            `;
        }
        tbody.innerHTML = out;
    }

    function escapeStr(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // Filter Memory Table
    $("#MemoryFilterInput").on("keyup", function () {
        let term = $(this).val().toLowerCase();
        $(".memory-row").each(function () {
            let text = $(this).text().toLowerCase();
            $(this).toggle(text.indexOf(term) > -1);
        });
    });

    // Refresh Memory button
    $("#RefreshMemoryBtn").click(function () {
        loadSearchMemory();
        swal("Refreshed", "Megatron Neural Memory feed updated.", "success");
    });

    // Clear All Memory button (strictly requires admin passcode)
    $("#ClearAllMemoryBtn").click(function () {
        swal({
            title: "Purge All Trained Memory?",
            text: "This action will permanently wipe all stored queries, answers, and learned weights.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        }).then((willDelete) => {
            if (willDelete) {
                eel.clearSearchMemory(currentAdminPasscode)(function (res) {
                    if (res === 1) {
                        loadSearchMemory();
                        swal("Purged", "Megatron Neural Memory wiped successfully.", "success");
                    } else {
                        swal("Access Denied", "Could not purge memory. Clearance required.", "error");
                    }
                });
            }
        });
    });

    // Re-run search from memory table
    $(document).on("click", ".run-memory-btn", function () {
        let q = $(this).attr("data-query");
        if (q) {
            let modalEl = document.getElementById('exampleModal');
            let settingsModal = bootstrap.Modal.getInstance(modalEl);
            if (settingsModal) settingsModal.hide();
            PlayAssistant(q);
        }
    });

    // Delete single memory record
    $(document).on("click", ".delete-memory-btn", function () {
        let id = $(this).attr("data-id");
        if (id) {
            eel.deleteSearchItem(id, currentAdminPasscode)(function (res) {
                if (res === 1) {
                    loadSearchMemory();
                }
            });
        }
    });

    // When settings modal tab is clicked
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        if (e.target.id === 'nav-memory-tab') {
            updateAdminVaultUI();
        } else if (e.target.id === 'nav-ai-tab') {
            loadApiConfig();
            updateTrainingStats();
        }
    });

    // Initial Vault UI sync on page load (starts locked by default)
    updateAdminVaultUI();

    // ========================================================
    // MULTI-PROVIDER API INTEGRATION & CONTINUOUS TRAINING
    // ========================================================
    let cachedApiConfig = {
        active_provider: "gemini",
        gemini_api_key: "",
        openai_api_key: "",
        groq_api_key: "",
        openrouter_api_key: "",
        custom_api_url: "http://localhost:11434/v1",
        custom_api_key: "",
        auto_failover: "1",
        quota_exhausted_providers: ""
    };

    let selectedProvider = "gemini";

    function loadApiConfig() {
        try {
            eel.getApiConfig()(function (jsonStr) {
                if (!jsonStr) return;
                try {
                    let data = JSON.parse(jsonStr);
                    cachedApiConfig = Object.assign(cachedApiConfig, data);
                    selectedProvider = cachedApiConfig.active_provider || "gemini";
                    applyProviderUI(selectedProvider);
                    $("#AutoFailoverSwitch").prop("checked", cachedApiConfig.auto_failover == "1" || cachedApiConfig.auto_failover === true);
                    updateQuotaWarnings();
                } catch (pe) {
                    console.log("API config parse error:", pe);
                }
            });
        } catch (err) {
            console.log("getApiConfig error:", err);
        }
    }

    function applyProviderUI(provider) {
        selectedProvider = provider;
        $(".provider-pill").removeClass("active");
        $(`.provider-pill[data-provider="${provider}"]`).addClass("active");

        let key = "";
        let providerName = "Google Gemini";
        if (provider === "gemini") {
            key = cachedApiConfig.gemini_api_key || "";
            providerName = "Google Gemini";
            $("#CustomEndpointBox").slideUp(150);
        } else if (provider === "openai") {
            key = cachedApiConfig.openai_api_key || "";
            providerName = "OpenAI (GPT-4o Mini)";
            $("#CustomEndpointBox").slideUp(150);
        } else if (provider === "groq") {
            key = cachedApiConfig.groq_api_key || "";
            providerName = "Groq Cloud (Llama 3.3)";
            $("#CustomEndpointBox").slideUp(150);
        } else if (provider === "openrouter") {
            key = cachedApiConfig.openrouter_api_key || "";
            providerName = "OpenRouter (DeepSeek / Claude / Llama)";
            $("#CustomEndpointBox").slideUp(150);
        } else if (provider === "custom") {
            key = cachedApiConfig.custom_api_key || "";
            providerName = "Custom / Local Endpoint (Ollama / vLLM)";
            $("#CustomApiUrlInput").val(cachedApiConfig.custom_api_url || "http://localhost:11434/v1");
            $("#CustomEndpointBox").slideDown(150);
        }

        $("#ActiveProviderLabel").html(`<i class="bi bi-key-fill text-warning me-1"></i> Attach ${providerName} Key`);
        $("#CurrentProviderApiKeyInput").val(key);
        updateActiveProviderStatusBadge();
    }

    function updateActiveProviderStatusBadge() {
        let exhaustedList = (cachedApiConfig.quota_exhausted_providers || "").split(",");
        let isExhausted = exhaustedList.indexOf(selectedProvider) > -1;
        let badge = $("#ActiveProviderStatusBadge");
        let currentKey = $("#CurrentProviderApiKeyInput").val().trim();

        if (isExhausted) {
            badge.removeClass("border-secondary text-muted border-success text-success")
                 .addClass("border-danger text-danger")
                 .html('<i class="bi bi-exclamation-triangle-fill me-1"></i> Package Quota Ended');
        } else if (currentKey.length > 0 || selectedProvider === "custom") {
            badge.removeClass("border-secondary text-muted border-danger text-danger")
                 .addClass("border-success text-success")
                 .html('<i class="bi bi-check-circle-fill me-1"></i> Key Attached');
        } else {
            badge.removeClass("border-danger text-danger border-success text-success")
                 .addClass("border-secondary text-muted")
                 .html('No Key Attached');
        }
    }

    function updateQuotaWarnings() {
        let exhaustedList = (cachedApiConfig.quota_exhausted_providers || "").split(",");
        $(".provider-pill").each(function () {
            let p = $(this).attr("data-provider");
            if (exhaustedList.indexOf(p) > -1) {
                $(this).find(".quota-ended-badge").remove();
                $(this).append('<span class="badge bg-danger quota-ended-badge ms-auto" style="font-size: 9px;">Quota Ended</span>');
            } else {
                $(this).find(".quota-ended-badge").remove();
            }
        });
        updateActiveProviderStatusBadge();
    }

    // Switch provider when clicked
    $(document).on("click", ".provider-pill", function () {
        let p = $(this).attr("data-provider");
        if (p) {
            // Save current input into cache first before switching
            let curKey = $("#CurrentProviderApiKeyInput").val().trim();
            if (selectedProvider === "gemini") cachedApiConfig.gemini_api_key = curKey;
            else if (selectedProvider === "openai") cachedApiConfig.openai_api_key = curKey;
            else if (selectedProvider === "groq") cachedApiConfig.groq_api_key = curKey;
            else if (selectedProvider === "openrouter") cachedApiConfig.openrouter_api_key = curKey;
            else if (selectedProvider === "custom") {
                cachedApiConfig.custom_api_key = curKey;
                cachedApiConfig.custom_api_url = $("#CustomApiUrlInput").val().trim();
            }
            cachedApiConfig.active_provider = p;
            applyProviderUI(p);
            $("#ApiTestFeedbackAlert").hide();
        }
    });

    // Toggle active API key visibility
    $("#ToggleActiveKeyVisBtn").click(function () {
        let input = $("#CurrentProviderApiKeyInput");
        let icon = $(this).find("i");
        if (input.attr("type") === "password") {
            input.attr("type", "text");
            icon.removeClass("bi-eye").addClass("bi-eye-slash");
        } else {
            input.attr("type", "password");
            icon.removeClass("bi-eye-slash").addClass("bi-eye");
        }
    });

    // Test API Connection & Quota Live Ping
    $("#TestConnectionBtn").click(function () {
        let p = selectedProvider;
        let key = $("#CurrentProviderApiKeyInput").val().trim();
        let customUrl = $("#CustomApiUrlInput").val().trim();

        $("#TestConnSpinner").show();
        $(this).attr("disabled", true);
        $("#ApiTestFeedbackAlert").hide();

        try {
            eel.testApiConnection(p, key, customUrl)(function (respStr) {
                $("#TestConnSpinner").hide();
                $("#TestConnectionBtn").attr("disabled", false);
                try {
                    let res = JSON.parse(respStr);
                    let alertBox = $("#ApiTestFeedbackAlert");
                    alertBox.removeClass("alert-success alert-danger alert-info").show();
                    if (res.success) {
                        alertBox.addClass("alert-success").html(`<i class="bi bi-check-circle-fill me-1"></i> ${res.message}`);
                        // Clear quota ended flag for this provider in cache
                        let list = (cachedApiConfig.quota_exhausted_providers || "").split(",").filter(x => x && x !== p);
                        cachedApiConfig.quota_exhausted_providers = list.join(",");
                        updateQuotaWarnings();
                    } else {
                        alertBox.addClass("alert-danger").html(`<i class="bi bi-x-circle-fill me-1"></i> ${res.message}`);
                    }
                } catch (e) {
                    $("#ApiTestFeedbackAlert").addClass("alert-info").text(respStr).show();
                }
            });
        } catch (err) {
            $("#TestConnSpinner").hide();
            $("#TestConnectionBtn").attr("disabled", false);
            $("#ApiTestFeedbackAlert").addClass("alert-danger").text("Test failed: " + err).show();
        }
    });

    // Attach & Save API Configuration
    $("#SaveApiConfigBtn").click(function () {
        let curKey = $("#CurrentProviderApiKeyInput").val().trim();
        if (selectedProvider === "gemini") cachedApiConfig.gemini_api_key = curKey;
        else if (selectedProvider === "openai") cachedApiConfig.openai_api_key = curKey;
        else if (selectedProvider === "groq") cachedApiConfig.groq_api_key = curKey;
        else if (selectedProvider === "openrouter") cachedApiConfig.openrouter_api_key = curKey;
        else if (selectedProvider === "custom") {
            cachedApiConfig.custom_api_key = curKey;
            cachedApiConfig.custom_api_url = $("#CustomApiUrlInput").val().trim();
        }
        cachedApiConfig.active_provider = selectedProvider;
        cachedApiConfig.auto_failover = $("#AutoFailoverSwitch").is(":checked") ? "1" : "0";

        try {
            eel.saveApiConfig(JSON.stringify(cachedApiConfig))(function (respStr) {
                try {
                    let res = JSON.parse(respStr);
                    if (res.success) {
                        swal("Key Attached!", `Megatron is now configured with active ${selectedProvider.toUpperCase()} provider. If your package ends, automatic failover keeps you protected.`, "success");
                        loadApiConfig();
                    } else {
                        swal("Save Failed", res.message || "Could not save configuration.", "error");
                    }
                } catch (e) {
                    swal("Saved", "API Configuration updated.", "success");
                }
            });
        } catch (err) {
            swal("Error", "Could not reach Megatron engine: " + err, "error");
        }
    });

    // Auto Failover Switch Toggle
    $("#AutoFailoverSwitch").change(function () {
        cachedApiConfig.auto_failover = $(this).is(":checked") ? "1" : "0";
        try {
            eel.saveApiConfig(JSON.stringify(cachedApiConfig))();
        } catch (e) { }
    });

    // Real-Time Continuous Training Stats Updater
    function updateTrainingStats() {
        try {
            eel.getTrainingStats()(function (statsJson) {
                if (!statsJson) return;
                try {
                    let stats = JSON.parse(statsJson);
                    $("#TrainedCountBadge").text(stats.trained_nodes || 0);
                    $("#ModelTrainedSearches").text(stats.searches || 0);
                    $("#ModelTrainedTopics").text(stats.topics || 0);
                    $("#ModelTrainedConfidence").text(stats.confidence ? stats.confidence + "x" : "1.0x");
                } catch (e) { }
            });
        } catch (e) { }
    }
    window.refreshTrainingStats = updateTrainingStats;

    // Direct Knowledge Training Submission
    $("#SubmitTrainFactBtn").click(function () {
        let topic = $("#TrainTopicInput").val().trim();
        let summary = $("#TrainSummaryInput").val().trim();
        if (!topic || !summary) {
            swal("Input Required", "Please provide both a topic/question and the fact/answer to train Megatron.", "warning");
            return;
        }

        try {
            eel.forceTrainEntry(topic, summary, "operator_train")(function (respStr) {
                try {
                    let res = JSON.parse(respStr);
                    if (res.success) {
                        $("#TrainTopicInput").val("");
                        $("#TrainSummaryInput").val("");
                        updateTrainingStats();
                        swal("Knowledge Node Trained!", "Megatron has integrated this verified knowledge into its continuous neural memory.", "success");
                    } else {
                        swal("Training Error", res.message || "Could not train node.", "error");
                    }
                } catch (e) {
                    swal("Trained", "Knowledge recorded into memory.", "success");
                    updateTrainingStats();
                }
            });
        } catch (err) {
            swal("Error", "Could not communicate with training engine.", "error");
        }
    });

    // Open API Integration Tab in Settings Modal
    function openApiIntegrationTab() {
        let settingsModalEl = document.getElementById('exampleModal');
        let modal = bootstrap.Modal.getOrCreateInstance(settingsModalEl);
        let aiTabTrigger = document.getElementById('nav-ai-tab');
        if (aiTabTrigger) {
            let tab = bootstrap.Tab.getOrCreateInstance(aiTabTrigger);
            tab.show();
        }
        modal.show();
        loadApiConfig();
        updateTrainingStats();
    }

    $("#ApiIntegrationBtn").click(openApiIntegrationTab);
    $("#QuickApiIntegrationBtn").click(openApiIntegrationTab);

    // Continuous Training Nodes click (Shows sleek info without locking modal)
    $("#HudTrainingPill").click(function () {
        let count = $("#TrainedCountBadge").text() || "0";
        swal({
            title: "Megatron Neural Memory",
            text: `Megatron continuous model training is active. Currently ${count} knowledge nodes have been learned and stored in memory. Every search and response compounds AI intelligence.`,
            icon: "info",
            button: "Acknowledge"
        });
    });

    // Modal fail-safe: clean up backdrops and restore body scrolling
    $(document).on('hidden.bs.modal', function () {
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css({
            'overflow-y': 'auto',
            'padding-right': '0'
        });
    });

    $(document).on('click', '[data-bs-dismiss="modal"]', function () {
        let modalEl = $(this).closest('.modal');
        if (modalEl.length > 0) {
            let inst = bootstrap.Modal.getInstance(modalEl[0]);
            if (inst) inst.hide();
        }
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css({
            'overflow-y': 'auto',
            'padding-right': '0'
        });
    });
    // Replay Live Response Voice
    $("#ReplayLiveVoiceBtn").click(function () {
        let text = $("#MegatronLiveResponseText").text();
        if (text && window.speakBrowserVoice) {
            window.speakBrowserVoice(text);
        }
    });

    // Copy Live Response Text
    $("#CopyLiveResponseBtn").click(function () {
        let text = $("#MegatronLiveResponseText").text();
        if (text && navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function () {
                swal("Copied", "Response text copied to clipboard.", "success");
            });
        }
    });

    // Dismiss Live Response Box
    $("#DismissLiveResponseBtn").click(function () {
        $("#MegatronLiveResponseBox").fadeOut(200);
    });

    // Software & Mobile APK Download Notifications
    $(document).on("click", "#QuickDownloadWindowsBtn, #HudDownloadWinBtn, #SuiteDownloadWinBtn, #CardDownloadWinBtn", function () {
        swal({
            title: "Downloading Windows Software Suite",
            text: "Megatron_Windows_Software_Suite.zip is downloading now. Extract the folder and run 'Setup_Megatron_Windows.bat' to unlock full PC hardware control!",
            icon: "success",
            timer: 4000,
            buttons: false
        });
    });

    $(document).on("click", "#QuickDownloadAndroidBtn, #HudDownloadApkBtn, #SuiteDownloadApkBtn, #CardDownloadApkBtn", function () {
        swal({
            title: "Downloading Android APK",
            text: "Megatron_Android_App.apk is downloading now. Transfer to your Android phone and install to unlock mobile device control!",
            icon: "success",
            timer: 4000,
            buttons: false
        });
    });

    // Optional Background Uninstallation Trigger (Kept safe if called programmatically)
    if ($("#TriggerSystemUninstallBtn").length) {
        $("#TriggerSystemUninstallBtn").click(function () {
            swal({
                title: "Completely Uninstall Megatron?",
                text: "WARNING: This will permanently stop all processes, remove shortcuts, delete all databases, and wipe all Megatron files from your computer so nothing remains.",
                icon: "warning",
                buttons: ["Cancel", "Yes, Delete Everything"],
                dangerMode: true,
            }).then(function (willUninstall) {
                if (willUninstall) {
                    swal("Uninstalling Megatron...", "The uninstaller script is purging all files from your system.", "info");
                    setTimeout(function () {
                        try {
                            eel.uninstallMegatronSystem()();
                        } catch (e) {
                            console.log("Uninstall call error:", e);
                        }
                    }, 1000);
                }
            });
        });
    }

    // Multi-Device Network Access Helper & Info
    function loadNetworkAccessInfo() {
        try {
            if (typeof eel !== "undefined" && eel.getNetworkAccessInfo) {
                eel.getNetworkAccessInfo()(function (info) {
                    if (info && info.network_url) {
                        window.megatronNetworkInfo = info;
                        $("#HudNetAccessText").text("ALL DEVICES: " + info.local_ip + ":" + info.port);
                        $("#NetworkAccessUrlInput").val(info.network_url);
                    }
                });
            }
        } catch (e) {
            console.log("Network info load error:", e);
        }
    }

    $(document).on("click", "#HudNetAccessBtn, #QuickAllDevicesBtn", function () {
        var host = (window.megatronNetworkInfo && window.megatronNetworkInfo.local_ip) 
                     ? window.megatronNetworkInfo.local_ip 
                     : (window.location.hostname === "localhost" ? "10.42.100.247" : window.location.hostname);
        var netUrl = "http://" + host + ":8000/index.html";
        swal({
            title: "Run Megatron on All Devices",
            text: "Connect any Android phone, iPhone, tablet, or PC to the same Wi-Fi and open in your browser:\n\n" + netUrl + "\n\n• Works instantly on all mobile browsers\n• Tap 'Install App' or 'Add to Home Screen' to install as full app\n• Downloads Windows Suite & Android APK directly to any device!",
            icon: "info",
            buttons: {
                copy: {
                    text: "Copy Network URL",
                    value: "copy",
                },
                close: {
                    text: "Got It",
                    value: false,
                }
            }
        }).then(function (val) {
            if (val === "copy") {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(netUrl);
                }
                swal("Copied to Clipboard!", netUrl, "success");
            }
        });
    });

    $(document).on("click", "#CopyNetworkUrlBtn", function () {
        var url = $("#NetworkAccessUrlInput").val();
        if (url) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url);
            }
            swal("Copied!", "Network URL copied to clipboard: " + url, "success");
        }
    });

    // Initial load on page ready
    loadApiConfig();
    updateTrainingStats();
    loadNetworkAccessInfo();

});

// Deletion helpers
function SysDeleteID(clicked_id) {
    eel.deleteSysCommand(clicked_id);
    setTimeout(function () {
        eel.displaySysCommand()();
    }, 200);
}

function WebDeleteID(clicked_id) {
    eel.deleteWebCommand(clicked_id);
    setTimeout(function () {
        eel.displayWebCommand()();
    }, 200);
}

function ContactDeleteID(clicked_id) {
    eel.deletePhoneBookCommand(clicked_id);
    setTimeout(function () {
        eel.displayPhoneBookCommand()();
    }, 200);
}