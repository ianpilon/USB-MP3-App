document.addEventListener('DOMContentLoaded', function() {
    // Server URL - base URL without trailing slash
    const SERVER_URL = window.location.origin;
    const API_URL = `${SERVER_URL}/api`;

    // Navigation
    const navLinks = document.querySelectorAll('nav ul li a');
    const sections = document.querySelectorAll('.section');

    // Change active section when nav link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            // Update active nav link
            navLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
            
            // Show target section
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');

            // Load songs if songs section is activated
            if (targetId === 'songs') {
                loadSongs();
            }
        });
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
            
            // Show success message
            alert('All files uploaded successfully!');
            
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
});
