const ResultsTable = ({ results, onAnalyze }) => {
  if (results.length === 0) {
    return (
      <div className="alert alert-light border text-center py-5 mt-4">
        <p className="mb-0 text-muted">No notes retrieved. Enter a query above to search the Vector DB.</p>
      </div>
    );
  }
  console.log('ResultsTable: received ${results}.. ')
  console.log(`ResultsTable: rendering components.. `)
  return (
    <div className="mt-5">
      <div className="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
        <h4 className="text-secondary">Search Results</h4>
        <span className="badge bg-secondary">{results.length} matches found</span>
      </div>

  
        {console.log(`ResultsTable: rendering table.. `)}
      <div className="table-responsive">
        <table className="table table-hover border shadow-sm bg-white">
          <thead className="table-light">
            <tr>
              <th>Title</th>
              <th>Note Snippet</th>
              <th>Tags</th>
              <th className="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {results.map((note) => (
              <tr key={note.id}>
                <td className="fw-bold">{note.title}</td>
                <td>
                  <div style={{ 
                    display: "-webkit-box", 
                    WebkitLineClamp: "2", 
                    WebkitBoxOrient: "vertical", 
                    overflow: "hidden",
                    fontSize: "0.85rem" 
                  }}>
                    {note.content}
                  </div>
                </td>
                <td>
                  {note.tags.map(tag => (
                    <span key={tag} className="badge rounded-pill bg-info text-dark me-1">
                      {tag}
                    </span>
                  ))}
                </td>
                <td className="text-center">
                  <button 
                    className="btn btn-sm btn-primary px-3"
                    onClick={() => onAnalyze(note)}
                  >
                    Analyze
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


export default ResultsTable

