import { useState } from 'react'

import {
    handlePopulateDBs,
    handleClearDBs, 
    analyzeTicket
} from '../services/api.jsx'

import ResultsTable from './ResultsTable.jsx'
import AnalysisModal from './AnalysisModal.jsx'


export default function App() {

    const [noteText,    setNoteText] = useState('')
    const [title,       setTitle] = useState('')
    const [tags,        setTags] = useState('')
    const [result,      setResult] = useState([])
    // Search & retrieval
    const [searchQuery, setSearchQuery] = useState ('')
    const [tagQuery,    setTagQuery]=useState('')


    //Analysis states
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
      const [isAnalyzing, setIsAnalyzing] = useState(false);
    
    const handleSubmit = async (e) => {
        // Stop the page from refreshing
        if (e) {
            e.preventDefault();  
        }
        const payload = {
            title: title,
            content: noteText,
            tags: tags.split(',').map(t => t.trim()).filter(t => t !== "")
        };

        try {
            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
            const response = await fetch(`${API_BASE_URL}/processTicket`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                console.log("Success! Ticket added to databases.");
                //DON'T call setTitle("") or setNoteText("") here 
                // since we want the text to stay visible for review.
            }
        } catch (error) {
            console.error("Submission failed:", error);
        }
    };

    const handleSearch = async (e) => {
        if (e) e.preventDefault();

        // Prepare tags (convert "tag1, tag2" to ["tag1", "tag2"])
        const tagsArray = tagQuery.split(',')
            .map(tag => tag.trim())
            .filter(tag => tag !== "");

        // Build the payload based on your datamodels.py structure
        const searchPayload = {
            query_text: searchQuery,
            tags: tagsArray,
        };

        console.log("Executing Hybrid Search with payload:", searchPayload);

        try {
            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
            const response = await fetch(`${API_BASE_URL}/retrieveTickets`, {                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(searchPayload),
            });

            if (!response.ok) {
                throw new Error(`Search failed: ${response.statusText}`);
            }

            const data = await response.json();
            setSearchQuery(searchQuery)
            setResult(data)
            //console.log("Search Results received:", data);
            
            // TODO: Update a state variable (e.g., setResults(data)) to display them in the UI
            
        } catch (err) {
            console.error("Retrieval Error:", err);
        }
    };    

    const handleAnalyze = async (note) => {
        setIsModalOpen(true); // Open immediately
        setIsAnalyzing(true);
        setAnalysisResult(null);
         console.log(`handleAnalyze: ${note.title} (ID: ${note.id})`);

        try {
            const response = await fetch('http://localhost:8000/analyzeTicket', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(note)
            });

            if (!response.ok) throw new Error("Backend analysis failed");

            const data = await response.json();
            console.log(`handleAnalyze received ${data.classification}`)
            // 2. Update state with the result from your classifier
            setAnalysisResult(data); 
        } catch (err) {
            console.error("Analysis Error:", err);
            setAnalysisResult("Error: could not reach the classifier.");
        } finally {
            // 3. Turn off the spinner
            setIsAnalyzing(false);
        }
    };

    // return the page
    return (
        <div className="container mt-4 mb-5">
            {/* TOP ROW: Global Actions */}
            <div className="row mb-2">
                <div className="col-12 d-flex align-items-center">
                <button className="btn btn-primary me-3" onClick={handlePopulateDBs}>
                    Load Samples
                </button>
                <button className="btn btn-outline-danger" onClick={handleClearDBs}>
                    Clear Samples
                </button>
                </div>
            </div>

            <hr className="my-4" />

            {/* MIDDLE ROW: The Input Form */}
            <div className="row justify-content-center">
                <div className="col-md-10"> 
                        <div className="mb-3">
                            <label className="form-label fw-bold">Note Title</label>
                            <input 
                            type="text" 
                            className="form-control" 
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Enter patient or case title..."
                            />
                        </div>

                    <div className="mb-3">
                        <label className="form-label fw-bold">Ticket Text</label>
                        <textarea 
                        className="form-control" 
                        rows="6" 
                        value={noteText}
                        onChange={(e) => setNoteText(e.target.value)}
                        placeholder="Paste medical notes here..."
                        ></textarea>
                    </div>

                    <div className="mb-3">
                        <label className="form-label fw-bold">Tags (comma separated)</label>
                        <input 
                        type="text" 
                        className="form-control" 
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        placeholder="cardiology, urgent, follow-up"
                        />
                    </div>

                    <button className="btn btn-success w-100 py-2 fw-bold" onClick={handleSubmit}>
                        Insert Into DB
                    </button>
                </div>
            </div>

            <hr className="my-5" />

            {/* BOTTOM ROW: Retrieval Section */}
            <div className="row justify-content-center">
                <div className="col-md-10">
                   
                    {/* Hybrid Retrieval Section */}
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <h3 className="mb-4 text-primary">Search & Retrieval</h3>
                            
                            <div className="card shadow-sm border-0 bg-light p-4">
                            {/* Text Search Query */}
                            <div className="mb-3">
                                <label className="form-label fw-bold">Semantic Query</label>
                                <input 
                                type="text" 
                                className="form-control form-control-lg" 
                                placeholder="Search symptoms, diagnosis, or patient history..." 
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <div className="form-text">Finds notes based on meaning and context.</div>
                            </div>

                            {/* Tag Filters */}
                            <div className="mb-4">
                                <label className="form-label fw-bold">Filter by Tags (comma separated)</label>
                                <input 
                                type="text" 
                                className="form-control" 
                                placeholder="e.g. cardiology, lab-results, priority-1" 
                                value={tagQuery}
                                onChange={(e) => setTagQuery(e.target.value)}
                                />
                                <div className="form-text">Narrow results by specific categories.</div>
                            </div>

                            {/* Single Search Action */}
                            <button className="btn btn-primary btn-lg w-100 fw-bold" onClick={handleSearch}>
                                Execute Search
                            </button>
                            </div>

                            <ResultsTable 
                                results={result} 
                                onAnalyze={handleAnalyze} 
                            />
                        
                            
                        </div>
                    </div>                
                </div>
            </div>

            <AnalysisModal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)} 
                data={analysisResult} 
                isLoading={isAnalyzing} 
                />
        </div> // This is the master container closure
    ) //return
} //App

