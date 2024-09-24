import React, { useState, useRef } from 'react';
import ReactJson from 'react-json-view';
import './ScrapeComponent.css';

const ScrapingComponent = () => {
  const [url, setUrl] = useState('');
  const [jsonData, setJsonData] = useState(null);
  const [logs, setLogs] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingLogs, setIsFetchingLogs] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const logsEndRef = useRef(null);

  const handleScrapeAndFetchLogs = async () => {
    const trimmedUrl = url.trim();
    if (!trimmedUrl) return;

    setIsLoading(true);
    setJsonData(null);
    setLogs('');
    setErrorMessage(null);

    // Start scraping immediately
    const scrapePromise = fetch(`http://127.0.0.1:5000/scrape-any/api/start?url=${encodeURIComponent(trimmedUrl)}`)
      .then(async (scrapeResponse) => {
        if (!scrapeResponse.ok) {
          throw new Error(`HTTP error! status: ${scrapeResponse.status}`);
        }
        return await scrapeResponse.json();
      })
      .then(result => setJsonData(result))
      .catch(error => {
        setErrorMessage(error.message);
        console.error('Error:', error);
      })
      .finally(() => {
        setIsLoading(false);
      });

    // Start fetching logs after a 10-second delay
    setTimeout(() => {
      const eventSource = new EventSource(`http://127.0.0.1:5000/logs?url=${encodeURIComponent(trimmedUrl)}`);

      eventSource.onmessage = (event) => {
        setLogs(prevLogs => prevLogs + event.data);
        scrollToBottom(); // Ensure logs container scrolls to the bottom
      };

      eventSource.onerror = (error) => {
        console.error('Error fetching logs:', error);
        setErrorMessage('Error fetching logs.');
        setIsFetchingLogs(false);
        eventSource.close();
      };

      eventSource.onopen = () => {
        console.log('Log stream opened.');
        setIsFetchingLogs(true);
      };

      // Close event source after scraping is done
      scrapePromise.finally(() => {
        setIsFetchingLogs(false);
        eventSource.close();
      });

    }, 10000); // 10 seconds delay

  };

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="scraping-page">
      <div className="form-container">
        <h1>Scrape Any Website</h1>
        <form onSubmit={(e) => e.preventDefault()}>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL to scrape"
            required
            className="input-url"
          />
          <button
            type="button"
            onClick={handleScrapeAndFetchLogs}
            className={`submit-btn ${isLoading || isFetchingLogs ? 'disabled' : ''}`}
            disabled={isLoading || isFetchingLogs || !url.trim()}
          >
            Start Scraping
          </button>
          {isLoading && <div className="loader"></div>}
          {isFetchingLogs && !isLoading && <div className="loader"></div>}
        </form>

        {/* Display error message if it exists */}
        {errorMessage && <div className="error-message">Error: {errorMessage}</div>}
      </div>

      {/* Display logs first */}
      {logs && (
        <div className="logs-container">
          <h2 className='live-logs'>Live Logs</h2>
          <pre>{logs}</pre>
          <div ref={logsEndRef} /> {/* Empty div to help scroll to the bottom */}
        </div>
      )}

      {/* Display scraped data after logs */}
      {jsonData && (
        <div className="json-container">
          <h2>Scraped Data</h2>
          <ReactJson src={jsonData} theme="monokai" collapsed={false} displayDataTypes={false} />
        </div>
      )}
    </div>
  );
};

export default ScrapingComponent;
