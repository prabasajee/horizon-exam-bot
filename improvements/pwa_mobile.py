"""
Progressive Web App (PWA) Configuration for Horizon Exam Bot
Includes service worker, offline capabilities, and mobile optimization
"""

# Service Worker JavaScript
SERVICE_WORKER_JS = '''
const CACHE_NAME = 'horizon-exam-bot-v1';
const OFFLINE_URL = '/offline.html';

// Files to cache for offline functionality
const CACHE_FILES = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/offline.html',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event - cache essential files
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Caching essential files');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;
    
    // Skip Chrome extension requests
    if (event.request.url.includes('chrome-extension')) return;
    
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // If request is successful, cache the response
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // If fetch fails, try to serve from cache
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            return response;
                        }
                        
                        // If not in cache and request is for a page, serve offline page
                        if (event.request.headers.get('accept').includes('text/html')) {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // For other requests, return a basic response
                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Background sync for offline form submissions
self.addEventListener('sync', event => {
    if (event.tag === 'quiz-submission') {
        event.waitUntil(syncQuizSubmissions());
    }
});

// Handle quiz submissions when back online
async function syncQuizSubmissions() {
    const db = await openIndexedDB();
    const submissions = await getOfflineSubmissions(db);
    
    for (const submission of submissions) {
        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(submission.data)
            });
            
            if (response.ok) {
                await removeOfflineSubmission(db, submission.id);
                console.log('Quiz submission synced:', submission.id);
            }
        } catch (error) {
            console.error('Failed to sync submission:', error);
        }
    }
}

// IndexedDB helper functions
function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('HorizonExamBot', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('offlineSubmissions')) {
                db.createObjectStore('offlineSubmissions', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

function getOfflineSubmissions(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['offlineSubmissions'], 'readonly');
        const store = transaction.objectStore('offlineSubmissions');
        const request = store.getAll();
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function removeOfflineSubmission(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['offlineSubmissions'], 'readwrite');
        const store = transaction.objectStore('offlineSubmissions');
        const request = store.delete(id);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}
'''

# Web App Manifest
MANIFEST_JSON = {
    "name": "Horizon Exam Bot",
    "short_name": "ExamBot",
    "description": "AI-powered study notes and quiz platform",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#667eea",
    "theme_color": "#667eea",
    "orientation": "portrait-primary",
    "categories": ["education", "productivity"],
    "lang": "en-US",
    "icons": [
        {
            "src": "/static/icons/icon-72x72.png",
            "sizes": "72x72",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-96x96.png",
            "sizes": "96x96",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-128x128.png",
            "sizes": "128x128",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-144x144.png",
            "sizes": "144x144",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-152x152.png",
            "sizes": "152x152",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-384x384.png",
            "sizes": "384x384",
            "type": "image/png"
        },
        {
            "src": "/static/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable"
        }
    ],
    "shortcuts": [
        {
            "name": "Create Notes",
            "short_name": "Notes",
            "description": "Generate study notes from documents",
            "url": "/?action=notes",
            "icons": [{"src": "/static/icons/notes-icon.png", "sizes": "96x96"}]
        },
        {
            "name": "Take Quiz",
            "short_name": "Quiz",
            "description": "Browse and take available quizzes",
            "url": "/quiz",
            "icons": [{"src": "/static/icons/quiz-icon.png", "sizes": "96x96"}]
        },
        {
            "name": "View Analytics",
            "short_name": "Analytics",
            "description": "View your learning analytics",
            "url": "/analytics",
            "icons": [{"src": "/static/icons/analytics-icon.png", "sizes": "96x96"}]
        }
    ]
}

# Enhanced Mobile CSS
MOBILE_CSS = '''
/* Mobile-First Responsive Design */
:root {
    --mobile-padding: 1rem;
    --mobile-margin: 0.5rem;
    --touch-target-size: 44px;
    --mobile-font-size: 16px;
}

/* Prevent zoom on form inputs on iOS */
input[type="text"],
input[type="email"],
input[type="password"],
textarea,
select {
    font-size: 16px !important;
}

/* Touch-friendly buttons */
.btn {
    min-height: var(--touch-target-size);
    min-width: var(--touch-target-size);
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    line-height: 1.5;
}

/* Mobile navigation */
@media (max-width: 768px) {
    .container {
        padding-left: var(--mobile-padding);
        padding-right: var(--mobile-padding);
    }
    
    .navbar-nav {
        margin-top: 1rem;
    }
    
    .navbar-nav .nav-link {
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Stack form elements vertically on mobile */
    .row.mobile-stack > [class*="col-"] {
        margin-bottom: 1rem;
    }
    
    /* Full-width cards on mobile */
    .card {
        margin-bottom: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Mobile-optimized modals */
    .modal-dialog {
        margin: 0.5rem;
        max-width: calc(100% - 1rem);
    }
    
    /* Hide unnecessary elements on mobile */
    .mobile-hide {
        display: none !important;
    }
    
    /* Show mobile-only elements */
    .mobile-show {
        display: block !important;
    }
    
    /* Mobile typography */
    h1 { font-size: 1.75rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.25rem; }
    
    /* Touch-friendly spacing */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .btn-group-vertical .btn {
        margin-bottom: 0.5rem;
    }
}

/* Tablet styles */
@media (min-width: 769px) and (max-width: 1024px) {
    .container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    .col-md-6 {
        flex: 0 0 50%;
        max-width: 50%;
    }
}

/* Large screen optimizations */
@media (min-width: 1200px) {
    .container {
        max-width: 1140px;
    }
    
    /* Show more content on larger screens */
    .large-screen-show {
        display: block !important;
    }
}

/* PWA-specific styles */
@media (display-mode: standalone) {
    /* Styles when app is installed as PWA */
    body {
        padding-top: env(safe-area-inset-top);
        padding-bottom: env(safe-area-inset-bottom);
    }
    
    .pwa-only {
        display: block !important;
    }
    
    .browser-only {
        display: none !important;
    }
}

/* Offline indicator */
.offline-indicator {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #dc3545;
    color: white;
    text-align: center;
    padding: 0.5rem;
    z-index: 9999;
    transform: translateY(-100%);
    transition: transform 0.3s ease;
}

.offline-indicator.show {
    transform: translateY(0);
}

/* Loading states */
.loading-skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Swipe gestures */
.swipe-container {
    position: relative;
    overflow: hidden;
    touch-action: pan-y;
}

.swipe-item {
    transition: transform 0.3s ease;
}

/* Voice input support */
.voice-input-btn {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #667eea;
}

.voice-input-btn.recording {
    color: #dc3545;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .card {
        border: 2px solid #000;
    }
    
    .btn {
        border: 2px solid currentColor;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --bs-body-bg: #121212;
        --bs-body-color: #ffffff;
        --bs-card-bg: #1e1e1e;
    }
    
    body {
        background-color: var(--bs-body-bg);
        color: var(--bs-body-color);
    }
    
    .card {
        background-color: var(--bs-card-bg);
        border-color: #333;
    }
    
    .navbar {
        background-color: #1e1e1e !important;
    }
}

/* Print styles */
@media print {
    .no-print {
        display: none !important;
    }
    
    .print-break {
        page-break-before: always;
    }
    
    a[href]:after {
        content: " (" attr(href) ")";
        font-size: 0.8em;
    }
}
'''

# Mobile JavaScript utilities
MOBILE_JS = '''
class MobileOptimizations {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupPWA();
        this.setupOfflineDetection();
        this.setupTouchGestures();
        this.setupVoiceInput();
        this.setupBackgroundSync();
    }
    
    setupPWA() {
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
        
        // PWA install prompt
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallButton();
        });
        
        // Show install button
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log('Install outcome:', outcome);
                    deferredPrompt = null;
                    this.hideInstallButton();
                }
            });
        }
    }
    
    setupOfflineDetection() {
        const offlineIndicator = document.createElement('div');
        offlineIndicator.className = 'offline-indicator';
        offlineIndicator.textContent = 'You are currently offline';
        document.body.appendChild(offlineIndicator);
        
        const updateOnlineStatus = () => {
            if (navigator.onLine) {
                offlineIndicator.classList.remove('show');
                this.syncOfflineData();
            } else {
                offlineIndicator.classList.add('show');
            }
        };
        
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
        updateOnlineStatus();
    }
    
    setupTouchGestures() {
        // Swipe gestures for quiz navigation
        let startX, startY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Only trigger if horizontal swipe is greater than vertical
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - next question
                    this.triggerNextQuestion();
                } else {
                    // Swipe right - previous question
                    this.triggerPreviousQuestion();
                }
            }
            
            startX = null;
            startY = null;
        });
    }
    
    setupVoiceInput() {
        if (!('webkitSpeechRecognition' in window)) return;
        
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        // Add voice input buttons to text inputs
        document.querySelectorAll('input[type="text"], textarea').forEach(input => {
            if (input.dataset.voiceDisabled) return;
            
            const container = document.createElement('div');
            container.style.position = 'relative';
            
            const voiceBtn = document.createElement('button');
            voiceBtn.type = 'button';
            voiceBtn.className = 'voice-input-btn';
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            
            input.parentNode.insertBefore(container, input);
            container.appendChild(input);
            container.appendChild(voiceBtn);
            
            voiceBtn.addEventListener('click', () => {
                recognition.start();
                voiceBtn.classList.add('recording');
            });
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                input.value = transcript;
                input.dispatchEvent(new Event('input'));
            };
            
            recognition.onend = () => {
                voiceBtn.classList.remove('recording');
            };
        });
    }
    
    setupBackgroundSync() {
        // Register for background sync when submitting forms offline
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            navigator.serviceWorker.ready.then(registration => {
                // Setup quiz submission sync
                const quizForms = document.querySelectorAll('form[data-sync="quiz"]');
                quizForms.forEach(form => {
                    form.addEventListener('submit', (e) => {
                        if (!navigator.onLine) {
                            e.preventDefault();
                            this.saveOfflineSubmission(form);
                            registration.sync.register('quiz-submission');
                        }
                    });
                });
            });
        }
    }
    
    async saveOfflineSubmission(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Save to IndexedDB
        const db = await this.openIndexedDB();
        const transaction = db.transaction(['offlineSubmissions'], 'readwrite');
        const store = transaction.objectStore('offlineSubmissions');
        
        await store.add({
            type: 'quiz-submission',
            data: data,
            timestamp: Date.now()
        });
        
        // Show user feedback
        this.showNotification('Your submission has been saved and will be sent when you\'re back online.');
    }
    
    async syncOfflineData() {
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            if (registration.sync) {
                registration.sync.register('quiz-submission');
            }
        }
    }
    
    openIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('HorizonExamBot', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            
            request.onupgradeneeded = event => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('offlineSubmissions')) {
                    db.createObjectStore('offlineSubmissions', { keyPath: 'id', autoIncrement: true });
                }
            };
        });
    }
    
    showInstallButton() {
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
        }
    }
    
    hideInstallButton() {
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }
    
    triggerNextQuestion() {
        const nextBtn = document.querySelector('.next-question-btn');
        if (nextBtn && !nextBtn.disabled) {
            nextBtn.click();
        }
    }
    
    triggerPreviousQuestion() {
        const prevBtn = document.querySelector('.prev-question-btn');
        if (prevBtn && !prevBtn.disabled) {
            prevBtn.click();
        }
    }
    
    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'info' ? 'primary' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container or create one
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    // Performance optimizations
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const lazyImages = document.querySelectorAll('img[data-src]');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        }
    }
    
    // Debounced search
    setupSearch() {
        const searchInputs = document.querySelectorAll('[data-search]');
        
        searchInputs.forEach(input => {
            let timeout;
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.performSearch(e.target.value, e.target.dataset.search);
                }, 300);
            });
        });
    }
    
    performSearch(query, type) {
        // Implement search based on type
        console.log(`Searching for: ${query} in ${type}`);
    }
}

// Initialize mobile optimizations when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MobileOptimizations();
});
'''

def setup_pwa_files(app):
    """Setup PWA files and routes"""
    from flask import Response, render_template_string
    
    @app.route('/sw.js')
    def service_worker():
        return Response(SERVICE_WORKER_JS, mimetype='application/javascript')
    
    @app.route('/manifest.json')
    def web_manifest():
        return jsonify(MANIFEST_JSON)
    
    @app.route('/offline.html')
    def offline_page():
        offline_html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Offline - Horizon Exam Bot</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                }
                .offline-container {
                    max-width: 400px;
                    padding: 2rem;
                }
                .offline-icon {
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }
                h1 { margin-bottom: 1rem; }
                p { margin-bottom: 2rem; opacity: 0.9; }
                .retry-btn {
                    background: rgba(255,255,255,0.2);
                    border: 2px solid white;
                    color: white;
                    padding: 0.75rem 2rem;
                    border-radius: 50px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                }
                .retry-btn:hover {
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">📱</div>
                <h1>You're Offline</h1>
                <p>No internet connection detected. Some features may not be available.</p>
                <a href="/" class="retry-btn" onclick="window.location.reload()">Try Again</a>
            </div>
        </body>
        </html>
        '''
        return render_template_string(offline_html)
    
    # Add PWA meta tags to base template
    @app.context_processor
    def inject_pwa_meta():
        pwa_meta = '''
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="ExamBot">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#667eea">
        <link rel="manifest" href="/manifest.json">
        <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
        '''
        return dict(pwa_meta=pwa_meta)
