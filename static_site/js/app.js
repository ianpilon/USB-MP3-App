document.addEventListener('DOMContentLoaded', function() {
    // Server URL
    const SERVER_URL = 'https://dj-usb-server-usb-mp3-app.onrender.com';

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

    // Load songs from server
    async function loadSongs() {
        try {
            songList.innerHTML = '<div class="loading">Loading songs...</div>';
            
            const response = await fetch(`${SERVER_URL}/songs`);
            if (!response.ok) {
                throw new Error('Failed to fetch songs');
            }
            
            const data = await response.json();
            
            if (data.songs.length === 0) {
                songList.innerHTML = '<div class="loading">No songs found</div>';
                return;
            }
            
            songList.innerHTML = '';
            
            data.songs.forEach(song => {
                const songItem = document.createElement('div');
                songItem.className = 'song-item';
                
                const title = song.title || song.filename;
                const artist = song.artist || 'Unknown artist';
                const album = song.album || 'Unknown album';
                
                songItem.innerHTML = `
                    <div class="song-info">
                        <div class="song-title">${title}</div>
                        <div class="song-artist">${artist} - ${album}</div>
                    </div>
                    <div class="song-actions">
                        <button class="play-song" data-url="${song.url}"><i class="fas fa-play"></i></button>
                        <button class="download-song" data-url="${song.url}"><i class="fas fa-download"></i></button>
                    </div>
                `;
                
                songList.appendChild(songItem);
            });
            
            // Add event listeners to play and download buttons
            document.querySelectorAll('.play-song').forEach(button => {
                button.addEventListener('click', function() {
                    const url = this.getAttribute('data-url');
                    playAudio(url);
                });
            });
            
            document.querySelectorAll('.download-song').forEach(button => {
                button.addEventListener('click', function() {
                    const url = this.getAttribute('data-url');
                    window.open(url, '_blank');
                });
            });
            
        } catch (error) {
            console.error('Error loading songs:', error);
            songList.innerHTML = `<div class="loading">Error loading songs: ${error.message}</div>`;
        }
    }

    // Play audio function
    function playAudio(url) {
        const audio = new Audio(url);
        audio.play();
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
