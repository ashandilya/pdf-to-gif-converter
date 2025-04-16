const config = {
    apiUrl: window.location.hostname.includes('vercel.app') || window.location.hostname.includes('localhost')
        ? `${window.location.protocol}//${window.location.hostname}/api`
        : 'http://localhost:8000'
};

export default config; 