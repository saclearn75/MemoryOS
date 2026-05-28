const AnalysisModal = ({ isOpen, onClose, data, isLoading }) => {
  if (!isOpen) return null;

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.7)' }}>
      <div className="modal-dialog modal-xl modal-dialog-centered">
        <div className="modal-content shadow border-0">
          <div className="modal-header bg-primary text-white">
            <h5 className="modal-title">Clinical Analysis Insight</h5>
            <button type="button" className="btn-close btn-close-white" onClick={onClose}></button>
          </div>
          
          <div className="modal-body bg-light p-4">
            {isLoading ? (
              <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status"></div>
                <p className="mt-3 text-muted">Analyzing medical context...</p>
              </div>
            ) : data ? (
              <div className="row g-3">
                {/* Section 1: Classification */}
                <div className="col-md-4">
                  <div className="card h-100 border-0 shadow-sm">
                    <div className="card-header bg-white fw-bold text-primary border-0">
                       Classification
                    </div>
                    <div className="card-body">
                      {Object.entries(data.classification).map(([key, value]) => (
                        <div key={key} className="mb-2">
                          <small className="text-uppercase text-muted fw-bold" style={{ fontSize: '0.7rem' }}>{key}</small>
                          <p className="mb-0">{String(value)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Section 2: Extracted Info */}
                <div className="col-md-4">
                  <div className="card h-100 border-0 shadow-sm">
                    <div className="card-header bg-white fw-bold text-success border-0">
                       Key Extractions
                    </div>
                    <div className="card-body">
                      {Object.entries(data.extracted_info).map(([key, value]) => (
                        <div key={key} className="mb-2">
                          <small className="text-uppercase text-muted fw-bold" style={{ fontSize: '0.7rem' }}>{key}</small>
                          <p className="mb-0 text-dark">{String(value)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Section 3: Recommendations */}
                <div className="col-md-4">
                  <div className="card h-100 border-0 shadow-sm border-start border-warning border-4">
                    <div className="card-header bg-white fw-bold text-warning-emphasis border-0">
                       Next Steps
                    </div>
                    <div className="card-body">
                      {Object.entries(data.recommendation).map(([key, value]) => (
                        <div key={key} className="mb-2">
                          <small className="text-uppercase text-muted fw-bold" style={{ fontSize: '0.7rem' }}>{key}</small>
                          <p className="mb-0 fst-italic">{String(value)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
          <div className="modal-footer border-0 bg-light">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Close Report</button>
          </div>
        </div>
      </div>
    </div>
  );
};



export default AnalysisModal