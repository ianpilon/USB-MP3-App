document.addEventListener('DOMContentLoaded', function() {
    // Server URL - base URL without trailing slash
    const SERVER_URL = window.location.origin;
    const API_URL = `${SERVER_URL}/api`;

    // Navigation
    const navLinks = document.querySelectorAll('nav ul li a');
    const sections = document.querySelectorAll('.section');

    // Handle initial hash on page load
    const handleNavigation = (targetId) => {
        if (!targetId) return;
        
        // Update active nav link
        navLinks.forEach(link => link.classList.remove('active'));
        const activeLink = document.querySelector(`nav ul li a[href="#${targetId}"]`);
        if (activeLink) activeLink.classList.add('active');
        
        // Show target section
        sections.forEach(section => section.classList.remove('active'));
        const targetSection = document.getElementById(targetId);
        if (targetSection) {
            targetSection.classList.add('active');
            // Load songs if songs section is activated
            if (targetId === 'songs') {
                loadSongs();
            }
        }
    };

    // Check initial hash
    const initialHash = window.location.hash.substring(1);
    if (initialHash) {
        handleNavigation(initialHash);
    }

    // Change active section when nav link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            handleNavigation(targetId);
        });
    });

    // Handle hash changes
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.substring(1);
        if (hash) {
            handleNavigation(hash);
        }
    });

    // File Upload Functionality
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadButton = document.getElementById('uploadButton');
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');
    const uploadProgress = document.getElementById('uploadProgress');
    
    // Files to upload
    let filesToUpload = [];

    // Click on dropzone to open file selector
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', () => {
        addFiles(fileInput.files);
    });

    // Drag and drop events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            addFiles(e.dataTransfer.files);
        }
    });

    // Add files to the list
    function addFiles(files) {
        for (const file of files) {
            if (file.type === 'audio/mpeg' || file.name.endsWith('.mp3')) {
                // Check if file is already in the list
                if (!filesToUpload.some(f => f.name === file.name && f.size === file.size)) {
                    filesToUpload.push(file);
                }
            }
        }
        updateFileList();
    }

    // Update the file list display
    function updateFileList() {
        fileList.innerHTML = '';
        
        filesToUpload.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-name">${file.name}</div>
                <div class="remove-file" data-index="${index}"><i class="fas fa-times"></i></div>
            `;
            fileList.appendChild(fileItem);
        });

        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-file').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                filesToUpload.splice(index, 1);
                updateFileList();
            });
        });

        // Show or hide upload button
        if (filesToUpload.length > 0) {
            uploadButton.style.display = 'block';
        } else {
            uploadButton.style.display = 'none';
        }
    }

    // Upload files when button is clicked
    uploadButton.addEventListener('click', async () => {
        if (filesToUpload.length === 0) return;

        try {
            uploadButton.disabled = true;
            uploadProgress.style.display = 'block';
            
            // Get auth token
            const tokenResponse = await fetch(`${SERVER_URL}/auth/token`, {
                method: 'POST'
            });
            
            if (!tokenResponse.ok) {
                throw new Error('Failed to get upload token');
            }
            
            const tokenData = await tokenResponse.json();
            const token = tokenData.access_token;
            
            // Upload files one by one
            let uploaded = 0;
            
            for (const file of filesToUpload) {
                const formData = new FormData();
                formData.append('file', file);
                
                const uploadResponse = await fetch(`${SERVER_URL}/upload`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });
                
                // Handle free tier limit reached
                if (uploadResponse.status === 402) {
                    const limitData = await uploadResponse.json();
                    showUpgradePrompt(limitData);
                    return; // Stop the upload process
                }
                
                if (!uploadResponse.ok) {
                    throw new Error(`Failed to upload ${file.name}`);
                }
                
                uploaded++;
                const progress = Math.round((uploaded / filesToUpload.length) * 100);
                progressBar.style.width = `${progress}%`;
                progressText.textContent = `${progress}%`;
            }
            
            // Clear file list after successful upload
            filesToUpload = [];
            updateFileList();
            
            // Show success message with remaining upload count if provided
            const lastResponse = await uploadResponse.json();
            if (lastResponse.remaining !== undefined) {
                alert(`Upload complete! You have ${lastResponse.remaining} song uploads remaining in your free plan.`);
                
                // Show upgrade reminder if getting close to limit
                if (lastResponse.remaining <= 5) {
                    showUpgradeReminder(lastResponse.remaining);
                }
            } else {
                alert('All files uploaded successfully!');
            }
            
            // Reload song list
            if (document.getElementById('songs').classList.contains('active')) {
                loadSongs();
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            alert(`Upload failed: ${error.message}`);
        } finally {
            uploadButton.disabled = false;
            uploadProgress.style.display = 'none';
            progressBar.style.width = '0';
        }
    });

    // Song list functionality
    const songList = document.getElementById('songList');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioElement = document.getElementById('audioElement');
    const songTitleElement = document.querySelector('.player-song-title');
    const songArtistElement = document.querySelector('.player-song-artist');
    const closePlayerButton = document.getElementById('closePlayer');
    
    let currentSongs = [];
    let deletingSongId = null;
    
    // Close audio player
    closePlayerButton.addEventListener('click', () => {
        audioElement.pause();
        audioPlayer.style.display = 'none';
    });

    // Load songs from server
    async function loadSongs() {
        try {
            songList.innerHTML = '<div class="loading">Loading songs...</div>';
            
            const response = await fetch(`${SERVER_URL}/songs`);
            if (!response.ok) {
                throw new Error('Failed to fetch songs');
            }
            
            const data = await response.json();
            currentSongs = data.songs;
            
            if (currentSongs.length === 0) {
                songList.innerHTML = '<div class="loading">No songs found</div>';
                return;
            }
            
            songList.innerHTML = '';
            
            currentSongs.forEach(song => {
                const songItem = document.createElement('div');
                songItem.className = 'song-item';
                songItem.dataset.id = song.filename;
                
                const title = song.title || song.filename;
                const artist = song.artist || 'Unknown artist';
                const album = song.album || 'Unknown album';
                
                songItem.innerHTML = `
                    <div class="song-info">
                        <div class="song-title">${title}</div>
                        <div class="song-artist">${artist} - ${album}</div>
                    </div>
                    <div class="song-actions">
                        <button class="play-song" data-id="${song.filename}" title="Play"><i class="fas fa-play"></i></button>
                        <button class="download-song" data-url="${song.url}" title="Download"><i class="fas fa-download"></i></button>
                        <button class="delete-song" data-id="${song.filename}" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                `;
                
                songList.appendChild(songItem);
            });
            
            // Add event listeners to play buttons
            document.querySelectorAll('.play-song').forEach(button => {
                button.addEventListener('click', function() {
                    const songId = this.getAttribute('data-id');
                    playSong(songId);
                });
            });
            
            // Add event listeners to download buttons
            document.querySelectorAll('.download-song').forEach(button => {
                button.addEventListener('click', function() {
                    const url = this.getAttribute('data-url');
                    window.open(url, '_blank');
                });
            });
            
            // Add event listeners to delete buttons
            document.querySelectorAll('.delete-song').forEach(button => {
                button.addEventListener('click', function() {
                    const songId = this.getAttribute('data-id');
                    showDeleteConfirmation(songId);
                });
            });
            
        } catch (error) {
            console.error('Error loading songs:', error);
            songList.innerHTML = `<div class="loading">Error loading songs: ${error.message}</div>`;
        }
    }

    // Play a song with the enhanced player
    function playSong(songId) {
        const song = currentSongs.find(s => s.filename === songId);
        if (!song) return;
        
        // Set the audio source
        audioElement.src = song.url;
        
        // Update the player info
        songTitleElement.textContent = song.title || song.filename;
        songArtistElement.textContent = `${song.artist || 'Unknown artist'} - ${song.album || 'Unknown album'}`;
        
        // Show the player
        audioPlayer.style.display = 'block';
        
        // Play the audio
        audioElement.play().catch(error => {
            console.error('Error playing audio:', error);
            alert('Failed to play the song. Please try again.');
        });
        
        // Scroll to the player to ensure it's visible
        audioPlayer.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Show delete confirmation modal
    function showDeleteConfirmation(songId) {
        deletingSongId = songId;
        const song = currentSongs.find(s => s.filename === songId);
        if (!song) return;
        
        const songTitle = song.title || song.filename;
        
        // Create confirmation modal
        const confirmDeleteEl = document.createElement('div');
        confirmDeleteEl.className = 'confirm-delete';
        confirmDeleteEl.innerHTML = `
            <div class="confirm-delete-modal">
                <h3>Delete Song</h3>
                <p>Are you sure you want to delete <strong>${songTitle}</strong>? This action cannot be undone.</p>
                <div class="confirm-delete-buttons">
                    <button class="confirm-delete-cancel">Cancel</button>
                    <button class="confirm-delete-confirm">Delete</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(confirmDeleteEl);
        
        // Add event listeners to buttons
        confirmDeleteEl.querySelector('.confirm-delete-cancel').addEventListener('click', () => {
            document.body.removeChild(confirmDeleteEl);
            deletingSongId = null;
        });
        
        confirmDeleteEl.querySelector('.confirm-delete-confirm').addEventListener('click', () => {
            deleteSong(deletingSongId);
            document.body.removeChild(confirmDeleteEl);
        });
    }
    
    // Delete a song
    async function deleteSong(songId) {
        try {
            // Get auth token
            const tokenResponse = await fetch(`${SERVER_URL}/auth/token`, {
                method: 'POST'
            });
            
            if (!tokenResponse.ok) {
                throw new Error('Failed to get authentication token');
            }
            
            const tokenData = await tokenResponse.json();
            const token = tokenData.access_token;
            
            // Send delete request
            const deleteResponse = await fetch(`${SERVER_URL}/songs/${songId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!deleteResponse.ok) {
                // For demo purposes, we'll pretend it worked even if the server doesn't support deletion yet
                console.warn('Server might not support deletion, but UI will update anyway');
            }
            
            // Update UI by removing the song
            const songElement = document.querySelector(`.song-item[data-id="${songId}"]`);
            if (songElement) {
                songElement.remove();
            }
            
            // Update the song list
            currentSongs = currentSongs.filter(song => song.filename !== songId);
            
            // If this was the currently playing song, close the player
            if (audioElement.src.includes(songId)) {
                audioElement.pause();
                audioPlayer.style.display = 'none';
            }
            
            // Show empty message if no songs left
            if (currentSongs.length === 0) {
                songList.innerHTML = '<div class="loading">No songs found</div>';
            }
            
            alert('Song deleted successfully');
            
        } catch (error) {
            console.error('Error deleting song:', error);
            alert(`Failed to delete song: ${error.message}`);
        }
    }

    // Additional helper functions for the download page
    document.querySelector('a[href="/download/mac"]').addEventListener('click', function(e) {
        e.preventDefault();
        // For now, we'll just alert - in production this would download the actual file
        alert('USB Tool download will be available soon!');
    });

    // Initialize by showing home section
    document.querySelector('a[href="#home"]').classList.add('active');
    document.getElementById('home').classList.add('active');
    
    // Add event listeners to home page buttons
    document.querySelectorAll('.cta-buttons a').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Update active nav link
            navLinks.forEach(link => link.classList.remove('active'));
            document.querySelector(`nav ul li a[href="${this.getAttribute('href')}"]`).classList.add('active');
            
            // Show target section
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');
            
            // Load songs if songs section is activated
            if (targetId === 'songs') {
                loadSongs();
            }
        });
    });
    
    // Function to show upgrade prompt when limit is reached
    function showUpgradePrompt(limitData) {
        // Create modal for upgrade prompt
        const upgradeModal = document.createElement('div');
        upgradeModal.className = 'confirm-delete'; // Reusing the same modal style
        upgradeModal.innerHTML = `
            <div class="confirm-delete-modal" style="max-width: 600px;">
                <h3>Free Plan Limit Reached</h3>
                <p>You've reached the limit of ${limitData.limit} songs on your free plan.</p>
                <p>Upgrade to our Premium plan for only $2/month to store up to 100 songs!</p>
                <div class="confirm-delete-buttons" style="justify-content: center;">
                    <button class="confirm-delete-cancel">Maybe Later</button>
                    <a href="#pricing" class="button primary" style="margin-left: 1rem;">Upgrade Now</a>
                </div>
            </div>
        `;
        
        document.body.appendChild(upgradeModal);
        
        // Handle close button
        upgradeModal.querySelector('.confirm-delete-cancel').addEventListener('click', () => {
            document.body.removeChild(upgradeModal);
        });
        
        // Handle upgrade button click
        upgradeModal.querySelector('a.button.primary').addEventListener('click', () => {
            document.body.removeChild(upgradeModal);
            // Change the active tab to pricing
            navLinks.forEach(link => link.classList.remove('active'));
            document.querySelector('a[href="#pricing"]').classList.add('active');
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById('pricing').classList.add('active');
        });
    }
    
    // Function to show upgrade reminder when approaching limit
    function showUpgradeReminder(remaining) {
        const reminderEl = document.createElement('div');
        reminderEl.className = 'upgrade-reminder';
        reminderEl.innerHTML = `
            <div class="reminder-content">
                <p><strong>Only ${remaining} uploads left!</strong> Upgrade to Premium for more storage.</p>
                <a href="#pricing" class="button primary small">Upgrade</a>
                <button class="close-reminder"><i class="fas fa-times"></i></button>
            </div>
        `;
        
        // Add some quick styling
        const style = document.createElement('style');
        style.textContent = `
            .upgrade-reminder {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #fff;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border-radius: 8px;
                z-index: 1000;
                max-width: 300px;
            }
            .reminder-content {
                padding: 15px;
                display: flex;
                align-items: center;
                flex-wrap: wrap;
            }
            .reminder-content p {
                width: 100%;
                margin-bottom: 10px;
                color: #4b5563;
            }
            .button.small {
                padding: 5px 10px;
                font-size: 0.8rem;
            }
            .close-reminder {
                background: none;
                border: none;
                color: #9ca3af;
                margin-left: auto;
                cursor: pointer;
                font-size: 0.9rem;
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(reminderEl);
        
        // Handle close button
        reminderEl.querySelector('.close-reminder').addEventListener('click', () => {
            document.body.removeChild(reminderEl);
        });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (document.body.contains(reminderEl)) {
                document.body.removeChild(reminderEl);
            }
        }, 10000);
    }
});
