import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import logoDark from './assets/logo-dark.png';
import logoLight from './assets/logo-light.png';
import { Analytics } from "@vercel/analytics/react"



import './App.css';

const ChartIcons = {
  Flowchart: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
      <path d="M5.25 8.625a2.625 2.625 0 115.25 0 2.625 2.625 0 01-5.25 0zM12 10.5v1.875c0 .207.168.375.375.375H16.5v1.5c0 .621-.504 1.125-1.125 1.125h-1.5v1.5h1.5a2.625 2.625 0 002.625-2.625v-1.5a.75.75 0 00-.75-.75h-3.75a.375.375 0 01-.375-.375V10.5h3c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-3v-.75A.75.75 0 0012 5.25h-1.875a.75.75 0 00-.75.75v.75h-3c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125h3zm-5.25 1.5a2.625 2.625 0 100 5.25 2.625 2.625 0 000-5.25zm10.5 0a2.625 2.625 0 100 5.25 2.625 2.625 0 000-5.25z" />
    </svg>
  ),
  Sequence: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
      <path fillRule="evenodd" d="M2.25 13.5a8.25 8.25 0 018.25-8.25.75.75 0 01.75.75v6.75H18a.75.75 0 01.75.75 8.25 8.25 0 01-16.5 0z" clipRule="evenodd" />
      <path fillRule="evenodd" d="M12.75 3a.75.75 0 01.75-.75 8.25 8.25 0 018.25 8.25.75.75 0 01-.75.75h-7.5a.75.75 0 01-.75-.75V3z" clipRule="evenodd" />
    </svg>
  ),
  Class: (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
      <path fillRule="evenodd" d="M1.5 5.625c0-1.036.84-1.875 1.875-1.875h17.25c1.035 0 1.875.84 1.875 1.875v12.75c0 1.035-.84 1.875-1.875 1.875H3.375A1.875 1.875 0 011.5 18.375V5.625zM21 9.375A.375.375 0 0020.625 9h-7.5a.375.375 0 00-.375.375v1.5c0 .207.168.375.375.375h7.5a.375.375 0 00.375-.375v-1.5zm0 3.75a.375.375 0 00-.375-.375h-7.5a.375.375 0 00-.375.375v1.5c0 .207.168.375.375.375h7.5a.375.375 0 00.375-.375v-1.5zm0 3.75a.375.375 0 00-.375-.375h-7.5a.375.375 0 00-.375.375v1.5c0 .207.168.375.375.375h7.5a.375.375 0 00.375-.375v-1.5zM10.875 18.75a.375.375 0 00.375-.375v-1.5a.375.375 0 00-.375-.375h-7.5a.375.375 0 00-.375.375v1.5c0 .207.168.375.375.375h7.5zM3.375 15h7.5a.375.375 0 00.375-.375v-1.5a.375.375 0 00-.375-.375h-7.5a.375.375 0 00-.375.375v1.5c0 .207.168.375.375.375zm0-3.75h7.5a.375.375 0 00.375-.375v-1.5A.375.375 0 0010.875 9h-7.5A.375.375 0 003 9.375v1.5c0 .207.168.375.375.375z" clipRule="evenodd" />
    </svg>
  )
};


const DefaultIcon = (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M2.25 13.5a8.25 8.25 0 018.25-8.25.75.75 0 01.75.75v6.75H18a.75.75 0 01.75.75 8.25 8.25 0 01-16.5 0z" clipRule="evenodd" />
    <path fillRule="evenodd" d="M12.75 3a.75.75 0 01.75-.75 8.25 8.25 0 018.25 8.25.75.75 0 01-.75.75h-7.5a.75.75 0 01-.75-.75V3z" clipRule="evenodd" />
  </svg>
);


const MoonIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
  </svg>
);

const SunIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
  </svg>
);

const InfoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
  </svg>
);

const QuestionMarkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
  </svg>
);

const MagicWandIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
  </svg>
);

const DownloadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
  </svg>
);

const CopyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75" />
  </svg>
);

const ShareIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935-2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />
  </svg>
);

const SpinnerIcon = () => (
  <svg className="animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

const SuccessIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const ErrorIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
  </svg>
);

const DiagramIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
  </svg>
);

const Sparkles = () => (
  <div className="sparkles">
    {[...Array(10)].map((_, i) => (
      <div 
        key={i} 
        className="sparkle" 
        style={{
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
          animationDelay: `${Math.random() * 2}s`,
          animationDuration: `${1 + Math.random() * 3}s`
        }}
      />
    ))}
  </div>
);

function App() {
  const [prompt, setPrompt] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [selectedChart, setSelectedChart] = useState(null);
  const [loadingMessage, setLoadingMessage] = useState('Generating your diagrams...');
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) return savedTheme;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });
  const [toasts, setToasts] = useState([]);
  const [isMagicEnhancing, setIsMagicEnhancing] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [promptHistory, setPromptHistory] = useState(() => {
    const savedHistory = localStorage.getItem('promptHistory');
    return savedHistory ? JSON.parse(savedHistory) : [];
  });
  const [showHistory, setShowHistory] = useState(false);
  const [showShareMenu, setShowShareMenu] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [highContrast, setHighContrast] = useState(() => {
    return localStorage.getItem('highContrast') === 'true';
  });
  const [showAccessibilityMenu, setShowAccessibilityMenu] = useState(false);
  const [showCredits, setShowCredits] = useState(false);
  
  const textareaRef = useRef(null);
  const toastTimeoutRef = useRef(null);
  
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-high-contrast', highContrast);
    localStorage.setItem('theme', theme);
    localStorage.setItem('highContrast', highContrast);
    
    // Announce theme change to screen readers
    const themeChangeMessage = `Theme changed to ${theme} mode${highContrast ? ' with high contrast' : ''}`;
    announceToScreenReader(themeChangeMessage);
  }, [theme, highContrast]);

  const announceToScreenReader = (message) => {
    const announcer = document.getElementById('screen-reader-announcer');
    if (announcer) {
      announcer.textContent = message;
    } else {
      const newAnnouncer = document.createElement('div');
      newAnnouncer.id = 'screen-reader-announcer';
      newAnnouncer.className = 'sr-only';
      newAnnouncer.setAttribute('aria-live', 'polite');
      newAnnouncer.textContent = message;
      document.body.appendChild(newAnnouncer);
    }
  };
  
  const toggleHighContrast = () => {
    const newContrast = !highContrast;
    setHighContrast(newContrast);
    document.documentElement.setAttribute('data-high-contrast', newContrast);
    localStorage.setItem('highContrast', String(newContrast));
  };
  
  const toggleAccessibilityMenu = () => {
    setShowAccessibilityMenu(prev => !prev);
  };
  
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  useEffect(() => {
    localStorage.setItem('promptHistory', JSON.stringify(promptHistory));
  }, [promptHistory]);

  useEffect(() => {
    if (isLoading) {
      const messages = [
        'Analyzing your request...',
        'Identifying optimal chart types...',
        'Generating sample data...',
        'Creating visualizations...',
        'Applying finishing touches...',
        'Almost there...'
      ];
      
      let index = 0;
      const interval = setInterval(() => {
        setLoadingMessage(messages[index % messages.length]);
        index++;
      }, 2500);
      
      return () => clearInterval(interval);
    }
  }, [isLoading]);
  
  
  useEffect(() => {
    if (toastTimeoutRef.current) {
      return () => clearTimeout(toastTimeoutRef.current)
    }
  }, []);

  // Verify connection to backend on mount
  useEffect(() => {
    const verifyBackendConnection = async () => {
      try {
        await axios.get('https://plott.onrender.com/cors-test', {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        console.log('Backend connection verified successfully');
      } catch (error) {
        console.error('Backend connection failed:', error);
        showToast(
          'API Connection Issue', 
          'Unable to connect to backend service. Please try again later or contact support if the issue persists.', 
          'warning'
        );
      }
    };
    
    verifyBackendConnection();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e) => {
      const isTextField = ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);
      
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && prompt.trim() && !isLoading) {
        e.preventDefault();
        handleSubmit(e);
      }
      
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        toggleHelp();
      }
      
      if ((e.metaKey || e.ctrlKey) && e.key === 'h') {
        e.preventDefault();
        toggleHistory();
      }
      
      if ((e.metaKey || e.ctrlKey) && e.key === 'e' && prompt.trim() && !isMagicEnhancing) {
        e.preventDefault();
        enhancePrompt(e);
      }
      
      if (e.key === 'Escape') {
        if (showHelp) {
          toggleHelp();
        } else if (showHistory) {
          toggleHistory();
        } else if (showShareMenu) {
          setShowShareMenu(false);
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [prompt, isLoading, isMagicEnhancing, showHelp, showHistory, showShareMenu]);

  const handlePromptChange = (e) => {
    const text = e.target.value;
    const words = text.trim() ? text.trim().split(/\s+/) : [];
    const count = words.length;
    
    if (count <= 150) {
      setPrompt(text);
      setWordCount(count);
    } else {
      // Don't update if word count exceeds 250
      e.preventDefault();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResult(null);
    setSelectedChart(null);
    
    try {
      console.log("Sending prompt to backend:", prompt);
      
      const trimmedPrompt = prompt.trim();
      if (!promptHistory.some(item => item.text === trimmedPrompt)) {
        setPromptHistory(prev => [
          { 
            id: Date.now(), 
            text: trimmedPrompt, 
            date: new Date().toISOString(),
            starred: false 
          }, 
          ...prev.slice(0, 19) 
        ]);
      }
      
      let response;
      try {
        response = await axios.post('https://plott.onrender.com/api/generate-diagram', { 
          prompt: trimmedPrompt 
        }, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        console.log("Flask backend response:", response.data);
      } catch (flaskError) {
        console.error('Flask backend error:', flaskError);
        response = await axios.post('/api/generate', { 
          prompt: trimmedPrompt 
        });
        console.log("Node.js backend response:", response.data);
      }
      
      const charts = response.data.charts.map(chart => ({
        type: chart.chart_type || chart.type,
        reason: chart.reason,
        image: chart.image.startsWith('http') 
          ? chart.image 
          : `data:image/png;base64,${chart.image}`,
      }));
      
      setResult({
        charts: charts,
        explanation: response.data.explanation || 'Diagram created based on your prompt.'
      });
      
      if (charts && charts.length > 0) {
        setSelectedChart(charts[0]);
      }
    } catch (err) {
      console.error('Generation error:', err);
      const errorMsg = err.response?.data?.message || err.response?.data?.error || 'An error occurred while generating the diagram';
      setError(errorMsg);
      showToast('Generation Failed', errorMsg, 'error');
    } finally {
      setIsLoading(false);
    }
  };
  
  const enhancePrompt = async (e) => {
    if (!prompt.trim() || isMagicEnhancing) return;
    
    setIsMagicEnhancing(true);
    const originalPrompt = prompt;
    
    try {
      console.log("Enhancing prompt:", originalPrompt);
      let response;
      try {
        response = await axios.post('https://plott.onrender.com/api/enhance-prompt', { 
          prompt: originalPrompt.trim() 
        }, {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        console.log("Enhance prompt response:", response.data);
        
        if (response.data.enhanced_prompt) {
          setPrompt(response.data.enhanced_prompt);
        } else if (response.data.result) {
          setPrompt(response.data.result);
        } else if (typeof response.data === 'string' && response.data.trim()) {
          setPrompt(response.data);
        } else {
          console.warn("Got invalid response from enhance-prompt", response.data);
          throw new Error("Received invalid response from server");
        }
      } catch (flaskError) {
        console.error('Flask backend error:', flaskError);
        response = await axios.post('/api/enhance-prompt', { 
          prompt: originalPrompt.trim() 
        });
        
        if (response.data.enhanced_prompt && response.data.enhanced_prompt.trim()) {
          setPrompt(response.data.enhanced_prompt);
        } else {
          throw new Error("Received invalid response from server");
        }
      }
      
      showToast('Prompt Enhanced', 'Your prompt has been magically improved!', 'success');
    } catch (err) {
      console.error('Error enhancing prompt:', err);
      setPrompt(originalPrompt);
      const errorMsg = err.response?.data?.message || err.response?.data?.error || 'Failed to enhance prompt';
      showToast('Enhancement Failed', errorMsg, 'error');
    } finally {
      setIsMagicEnhancing(false);
    }
  };

  const toggleHelp = () => {
    setShowHelp(prev => !prev);
  };
  
  const toggleHistory = () => {
    setShowHistory(prev => !prev);
  };
  
  const useFromHistory = (historyItem) => {
    setPrompt(historyItem.text);
    setShowHistory(false);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };
  
  const toggleStarPrompt = (id) => {
    setPromptHistory(prev => 
      prev.map(item => 
        item.id === id ? { ...item, starred: !item.starred } : item
      )
    );
  };
  
  const deleteFromHistory = (id) => {
    setPromptHistory(prev => prev.filter(item => item.id !== id));
  };
  
  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear your prompt history?')) {
      setPromptHistory([]);
      setShowHistory(false);
    }
  };
  
  const showToast = (title, message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, title, message, type }]);
    
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 3000);
  };
  
  const downloadImage = (imageUrl, chartType) => {
    if (!imageUrl) return;
    
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `diagram-${chartType}-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Download Complete', 'Image saved to your downloads folder', 'success');
  };
  
  const copyImageToClipboard = async (imageUrl) => {
    if (!imageUrl) return;
    
    try {
      setIsCopying(true);
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const item = new ClipboardItem({ 'image/png': blob });
      await navigator.clipboard.write([item]);
      showToast('Copied!', 'Diagram copied to clipboard', 'success');
      
      setTimeout(() => {
        setIsCopying(false);
      }, 1500);
    } catch (err) {
      console.error('Failed to copy image:', err);
      showToast('Copy Failed', 'Unable to copy image to clipboard', 'error');
      setIsCopying(false);
    }
  };
  
  const getChartIcon = (type) => {
    return ChartIcons[type] || DefaultIcon;
  };

  const shareImage = async (imageUrl, chartType) => {
    if (!imageUrl) return;
    
    if (navigator.share) {
      try {
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const file = new File([blob], `diagram-${chartType}.png`, { type: 'image/png' });
        
        await navigator.share({
          title: 'Check out my diagram!',
          text: `I created this ${chartType} diagram with Plott.`,
          files: [file]
        });
        
        showToast('Shared!', 'Diagram shared successfully', 'success');
      } catch (err) {
        console.error('Share error:', err);
        if (err.name !== 'AbortError') {
          showToast('Share Failed', 'Unable to share diagram', 'error');
        }
      }
    } else {
      setShowShareMenu(prev => !prev);
    }
  };
  
  const shareToTwitter = (imageUrl, chartType) => {
    const text = encodeURIComponent(`I created this ${chartType} diagram with Plott. #DataVisualization`);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(window.location.href)}`, '_blank');
    setShowShareMenu(false);
  };
  
  const shareToFacebook = () => {
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`, '_blank');
    setShowShareMenu(false);
  };
  
  const shareToLinkedIn = () => {
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`, '_blank');
    setShowShareMenu(false);
  };

  return (
    
    <div className="app-container">
      <div className="gradient-bg">
        <div className="gradient-overlay"></div>
      </div>
      
      <motion.header 
        className="app-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="logo-container">
        <img 
  src={theme === 'light' ? logoDark : logoLight} 
  alt="Plott Logo" 
  className="logo-image" 
/>

        </div>
        
        <div className="header-actions">
          <button 
            className="theme-toggle" 
            onClick={toggleTheme} 
            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          >
            {theme === 'light' ? <MoonIcon /> : <SunIcon />}
          </button>
        </div>
      </motion.header>

      <AnimatePresence>
        {showHelp && (
          <motion.div 
            className="help-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleHelp}
          >
            <motion.div 
              className="help-modal"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="help-modal-header">
                <h2>How to Use Plott</h2>
                <button 
                  className="help-close-btn" 
                  onClick={toggleHelp}
                  aria-label="Close help"
                >
                  &times;
                </button>
              </div>
              <div className="help-modal-content">
                <h3>What is Plott?</h3>
                <p>
                  Plott is an AI-powered diagram generator that turns your text descriptions into beautiful visualizations.
                  No coding or spreadsheet skills required - just describe what you want to see!
                </p>
                
                <h3>How to Get Started</h3>
                <ol>
                  <li>
                    <strong>Describe Your Visualization</strong>
                    <p>Enter a prompt describing the data you want to visualize. Be specific about what relationships or patterns you want to highlight.</p>
                  </li>
                  <li>
                    <strong>Enhance with AI (Optional)</strong>
                    <p>Click the magic wand button to let our AI improve your prompt for better results.</p>
                  </li>
                  <li>
                    <strong>Generate Visualizations</strong>
                    <p>Click "Create Visualization" and wait a few seconds for our AI to generate multiple diagram options.</p>
                  </li>
                  <li>
                    <strong>Select and Download</strong>
                    <p>Choose your preferred diagram from the options. You can download it or copy it to your clipboard.</p>
                  </li>
                </ol>
                
                <h3>Tips for Better Results</h3>
                <ul>
                  <li>Be specific about the type of data and relationships you want to visualize</li>
                  <li>Mention the chart type if you have a preference (bar, line, pie, flowchart, etc.)</li>
                  <li>Include time periods, categories, or metrics if relevant</li>
                  <li>Use the AI enhancement feature if you're not sure how to phrase your request</li>
                </ul>
                
                <h3>Example Prompts</h3>
                <ul>
                  <li>"Create a flowchart showing the customer onboarding process from signup to first purchase"</li>
                  <li>"Compare quarterly sales performance across departments using a bar chart"</li>
                  <li>"Show the distribution of budget allocation across marketing channels"</li>
                </ul>
                
                <div className="keyboard-shortcuts">
                  <h3>Keyboard Shortcuts</h3>
                  <div className="shortcut-grid">
                    <div className="shortcut-item">
                      <span className="shortcut-desc">Generate visualization</span>
                      <div className="shortcut-combo">
                        <span className="key">Ctrl</span>
                        <span>+</span>
                        <span className="key">Enter</span>
                      </div>
                    </div>
                    <div className="shortcut-item">
                      <span className="shortcut-desc">Enhance prompt</span>
                      <div className="shortcut-combo">
                        <span className="key">Ctrl</span>
                        <span>+</span>
                        <span className="key">E</span>
                      </div>
                    </div>
                    <div className="shortcut-item">
                      <span className="shortcut-desc">Toggle help</span>
                      <div className="shortcut-combo">
                        <span className="key">Ctrl</span>
                        <span>+</span>
                        <span className="key">/</span>
                      </div>
                    </div>
                    <div className="shortcut-item">
                      <span className="shortcut-desc">View prompt history</span>
                      <div className="shortcut-combo">
                        <span className="key">Ctrl</span>
                        <span>+</span>
                        <span className="key">H</span>
                      </div>
                    </div>
                    <div className="shortcut-item">
                      <span className="shortcut-desc">Close dialogs</span>
                      <div className="shortcut-combo">
                        <span className="key">Esc</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showHistory && (
          <motion.div 
            className="help-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleHistory}
          >
            <motion.div 
              className="help-modal history-modal"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="help-modal-header">
                <h2>Your Prompt History</h2>
                <div className="history-header-actions">
                  {promptHistory.length > 0 && (
                    <button 
                      className="clear-history-btn" 
                      onClick={clearHistory}
                    >
                      Clear All
                    </button>
                  )}
                  <button 
                    className="help-close-btn" 
                    onClick={toggleHistory}
                    aria-label="Close history"
                  >
                    &times;
                  </button>
                </div>
              </div>
              <div className="help-modal-content">
                {promptHistory.length === 0 ? (
                  <div className="empty-history">
                    <p>Your prompt history will appear here.</p>
                    <p>Start by creating your first visualization!</p>
                  </div>
                ) : (
                  <div className="history-list">
                    {promptHistory.map(item => (
                      <div key={item.id} className="history-item">
                        <div className="history-item-content" onClick={() => useFromHistory(item)}>
                          <p className="history-text">{item.text}</p>
                          <span className="history-date">
                            {new Date(item.date).toLocaleDateString()} at {new Date(item.date).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="history-item-actions">
                          <button 
                            className={`star-button ${item.starred ? 'starred' : ''}`}
                            onClick={() => toggleStarPrompt(item.id)}
                            aria-label={item.starred ? "Unstar prompt" : "Star prompt"}
                          >
                            {item.starred ? (
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                                <path fillRule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clipRule="evenodd" />
                              </svg>
                            ) : (
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                              </svg>
                            )}
                          </button>
                          <button 
                            className="delete-button"
                            onClick={() => deleteFromHistory(item.id)}
                            aria-label="Delete prompt"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        className="info-button"
        onClick={toggleHelp}
        aria-label="Help information"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <QuestionMarkIcon />
      </motion.button>
      
      <motion.button
        className="history-button"
        onClick={toggleHistory}
        aria-label="View prompt history"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </motion.button>
      
      <motion.button
        className="accessibility-button"
        onClick={toggleAccessibilityMenu}
        aria-label="Accessibility options"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
        </svg>
      </motion.button>

      <main className="main-content">
        <motion.section 
          className="input-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <div className="input-header">
            <h2 className="input-title">Describe Your Vision</h2>
            <p className="input-description">
            No spreadsheets, no code. Just describe what you need visualized, and we'll handle the rest.            </p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className={`input-wrapper ${isFocused ? 'focused' : ''}`}>
              <textarea
                ref={textareaRef}
                className="prompt-input"
                value={prompt}
                onChange={handlePromptChange}
                placeholder="E.g., Compare department revenue, track yearly profit, and show product category share – bar, line, pie"
                rows="5"
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
              />
              
              <div className="word-counter">
                <span className={wordCount >= 150 ? 'limit-reached' : ''}>
                  {wordCount}/150 words
                </span>
              </div>
              
              <motion.button 
                type="button" 
                className="magic-button" 
                onClick={enhancePrompt}
                disabled={!prompt.trim() || isMagicEnhancing}
                aria-label="Enhance prompt with AI"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isMagicEnhancing ? (
                  <SpinnerIcon />
                ) : (
                  <>
                    <MagicWandIcon />
                    <Sparkles />
                  </>
                )}
                <span className="magic-tooltip">Enhance with AI</span>
              </motion.button>
            </div>
            
            <motion.button 
              type="submit" 
              className="submit-btn"
              disabled={isLoading || !prompt.trim() || isMagicEnhancing}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <>
                  <SpinnerIcon />
                  Generating...
                </>
              ) : (
                <>Create Visualization</>
              )}
            </motion.button>
          </form>
        </motion.section>
        
        <AnimatePresence>
          {error && (
            <motion.div 
              className="alert alert-danger"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="alert-title">Error</div>
              {error}
            </motion.div>
          )}
        </AnimatePresence>
        
        <AnimatePresence>
          {isLoading && (
            <motion.div 
              className="loading-container"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="loading-spinner">
                <div className="spinner-circle"></div>
                <div className="spinner-circle"></div>
                <div className="spinner-circle"></div>
              </div>
              <p className="loading-text">{loadingMessage}</p>
            </motion.div>
          )}
        </AnimatePresence>
        
        <AnimatePresence>
          {result && !isLoading && result.charts && result.charts.length > 0 && (
            <motion.div 
              className="result-container"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="results-header">
                <h2 className="results-title">Your Generated Visualizations</h2>
                <p className="results-subtitle">Select a diagram to view details and download options</p>
              </div>
              
              {result.error_messages && (
                <div className="alert alert-warning">
                  <div className="alert-title">Some diagrams couldn't be generated:</div>
                  <ul>
                    {Array.isArray(result.error_messages) ? 
                      result.error_messages.map((msg, i) => <li key={i}>{msg}</li>) :
                      <li>{result.error_messages}</li>
                    }
                  </ul>
                </div>
              )}
              
              <div className="chart-selector">
                <div className="row g-3">
                  {result.charts.map((chart, index) => (
                    <div className="col-md-4" key={index}>
                      <motion.div 
                        className={`chart-option ${selectedChart && selectedChart.type === chart.type ? 'selected' : ''}`}
                        onClick={() => setSelectedChart(chart)}
                        whileHover={{ y: -5 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div className="chart-header">
                          <div className="chart-title">
                            <span className="chart-icon">
                              {getChartIcon(chart.type)}
                            </span>
                            {chart.type} Diagram
                            {selectedChart && selectedChart.type === chart.type && (
                              <span className="chart-badge">Selected</span>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    </div>
                  ))}
                </div>
              </div>
              
              {selectedChart && (
                <motion.div 
                  className="chart-display"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="chart-display-header">
                    <h3 className="chart-display-title">
                      <span className="chart-icon">
                        {getChartIcon(selectedChart.type)}
                      </span>
                      {selectedChart.type} Diagram
                    </h3>
                    
                    <div className="chart-actions">
                      <motion.button 
                        className="chart-action-btn" 
                        onClick={() => downloadImage(selectedChart.image, selectedChart.type)}
                        aria-label="Download diagram"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <DownloadIcon />
                        <span>Download</span>
                      </motion.button>
                      
                      <motion.button 
                        className={`chart-action-btn ${isCopying ? 'copied' : ''}`}
                        onClick={() => copyImageToClipboard(selectedChart.image)}
                        aria-label="Copy diagram to clipboard"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        disabled={isCopying}
                      >
                        {isCopying ? (
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="check-icon">
                            <path fillRule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <CopyIcon />
                        )}
                        <span>{isCopying ? 'Copied!' : 'Copy'}</span>
                      </motion.button>
                      
                      <div className="share-container">
                        <motion.button 
                          className="chart-action-btn" 
                          onClick={() => shareImage(selectedChart.image, selectedChart.type)}
                          aria-label="Share diagram"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <ShareIcon />
                          <span>Share</span>
                        </motion.button>
                        
                        {showShareMenu && (
                          <div className="share-menu">
                            <button 
                              className="share-option" 
                              onClick={() => shareToTwitter(selectedChart.image, selectedChart.type)}
                            >
                              <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" className="twitter-icon">
                                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                              </svg>
                              <span>Twitter</span>
                            </button>
                            <button 
                              className="share-option" 
                              onClick={shareToFacebook}
                            >
                              <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" className="facebook-icon">
                                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                              </svg>
                              <span>Facebook</span>
                            </button>
                            <button 
                              className="share-option" 
                              onClick={shareToLinkedIn}
                            >
                              <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" className="linkedin-icon">
                                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                              </svg>
                              <span>LinkedIn</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="chart-display-body">
                    <motion.div 
                      className="diagram-image-container"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}
                    >
                      <img 
                        src={selectedChart.image} 
                        alt={`${selectedChart.type} diagram`} 
                        className="diagram-image"
                      />
                    </motion.div>
                  </div>
                  
                  <div className="chart-info">
                    <div className="chart-info-header">
                      <h4 className="chart-info-title">Diagram Details</h4>
                    </div>
                    <div className="chart-info-body">
                      <div className="chart-detail">
                        <div className="chart-detail-label">Type</div>
                        <div className="chart-detail-value">{selectedChart.type}</div>
                      </div>
                      <div className="chart-detail">
                        <div className="chart-detail-label">Explanation</div>
                        <div className="chart-detail-value">{selectedChart.reason}</div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
      
      <div className="toast-container">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div 
              key={toast.id} 
              className={`toast ${toast.type}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <span className="toast-icon">
                {toast.type === 'success' && <SuccessIcon />}
                {toast.type === 'error' && <ErrorIcon />}
              </span>
              <div className="toast-content">
                <div className="toast-title">{toast.title}</div>
                <div className="toast-message">{toast.message}</div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      
      <AnimatePresence>
        {showAccessibilityMenu && (
          <motion.div 
            className="accessibility-menu"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <div className="accessibility-menu-header">
              <h3>Accessibility Options</h3>
              <button 
                className="accessibility-close-btn" 
                onClick={toggleAccessibilityMenu}
                aria-label="Close accessibility menu"
              >
                &times;
              </button>
            </div>
            <div className="accessibility-menu-content">
              <div className="accessibility-option">
                <label>High Contrast Mode</label>
                <div className="toggle-switch-container" onClick={toggleHighContrast}>
                  <div className={`toggle-switch ${highContrast ? 'active' : ''}`} role="switch" aria-checked={highContrast}>
                    <span className="toggle-slider"></span>
                  </div>
                </div>
              </div>
              <div className="accessibility-option">
                <label>Dark Mode</label>
                <div className="toggle-switch-container" onClick={toggleTheme}>
                  <div className={`toggle-switch ${theme === 'dark' ? 'active' : ''}`} role="switch" aria-checked={theme === 'dark'}>
                    <span className="toggle-slider"></span>
                  </div>
                </div>
              </div>
              <div className="accessibility-info">
                <p>You can also use the following keyboard shortcuts:</p>
                <ul>
                  <li><strong>Ctrl + /</strong> - Open help</li>
                  <li><strong>Ctrl + H</strong> - View prompt history</li>
                  <li><strong>Ctrl + Enter</strong> - Generate visualization</li>
                  <li><strong>Esc</strong> - Close any open dialog</li>
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      <div id="screen-reader-announcer" className="sr-only" aria-live="polite"></div>
      
      {/* Credits button */}
      <button 
        className="credits-button" 
        onClick={() => setShowCredits(prev => !prev)}
        aria-label="View credits and information"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
        </svg>
      </button>
      
      <AnimatePresence>
        {showCredits && (
          <motion.div 
            className="credits-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowCredits(false)}
          >
            <motion.div 
              className="credits-modal"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onClick={e => e.stopPropagation()}
            >
              <button 
                className="credits-close-btn" 
                onClick={() => setShowCredits(false)}
                aria-label="Close credits"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              
              <div className="credits-content">
                <h2>Our Story</h2>
                <p>
                  Plott was born from the idea that creating diagrams shouldn't be complicated. Instead of relying on clunky software or manual drawing tools, we set out to design a smarter way, an AI-powered platform that transforms plain text into clear, expressive visuals. The mission: make visual storytelling easy and accessible for everyone.
                </p>
                
                <h2>What is Plott?</h2>
                <p>
                  Plott is a free, open-source tool that turns simple text into clean, professional diagrams. Just type what you need to visualize, no coding, no cluttered interfaces. Fast, effortless, and user-friendly.
                </p>
                
                <h2>Made by</h2>
                <div className="creators-list">
                  <div className="creator-item">
                    <span>Hitasnhu Gala</span>
                    <a href="https://github.com/indra55" target="_blank" rel="noopener noreferrer">
                      <svg fill="currentColor" viewBox="0 0 24 24">
                        <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                      </svg>
                    </a>
                  </div>
                </div>
                
                <div className="copyright">
                  © {new Date().getFullYear()}. All rights reserved. The developer disclaims any liability for inappropriate or unintended use of this software.
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <Analytics/>
    </div>
    
  );
}

export default App;