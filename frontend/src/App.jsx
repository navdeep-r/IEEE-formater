import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [formData, setFormData] = useState({
    title: '',
    paperNotice: '',
    funding: '',
    dropCap: true,
    authors: [{ firstName: '', lastName: '', membership: '', department: '', organization: '', cityCountry: '', email: '' }],
    abstract: '',
    keywords: '',
    sections: [
      { title: 'Introduction', content: '' },
      { title: 'Section II', content: '', subsections: [] }
    ],
    references: ''
  });

  const [pdfUrl, setPdfUrl] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAuthorChange = (index, field, value) => {
    const updatedAuthors = [...formData.authors];
    updatedAuthors[index][field] = value;
    setFormData(prev => ({
      ...prev,
      authors: updatedAuthors
    }));
  };

  const addAuthor = () => {
    if (formData.authors.length < 6) {
      setFormData(prev => ({
        ...prev,
        authors: [...prev.authors, { firstName: '', lastName: '', membership: '', department: '', organization: '', cityCountry: '', email: '' }]
      }));
    }
  };

  const removeAuthor = (index) => {
    if (formData.authors.length > 1) {
      const updatedAuthors = formData.authors.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        authors: updatedAuthors
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Send form data to backend to generate PDF
      const response = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        setPdfUrl(url);
      } else {
        console.error('Error generating PDF');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const downloadPdf = () => {
    if (pdfUrl) {
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = 'ieee_conference_paper.pdf';
      link.click();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>IEEE Conference Paper Generator</h1>
        <p>Fill in the form below to generate a properly formatted IEEE conference paper</p>
      </header>
      
      <main className="main-content">
        <form onSubmit={handleSubmit} className="paper-form">
          {/* Paper Title */}
          <div className="form-section">
            <h2>Paper Metadata</h2>
            <div className="input-group">
              <label htmlFor="title">Conference Paper Title *</label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter paper title (no symbols or special characters)"
                required
              />
              <p className="field-note">Note: Sub-titles are not captured for https://ieeexplore.ieee.org and should not be used.</p>
            </div>
            <div className="input-group">
              <label htmlFor="paperNotice">Special Paper Notice</label>
              <input
                type="text"
                id="paperNotice"
                value={formData.paperNotice}
                onChange={(e) => handleInputChange('paperNotice', e.target.value)}
                placeholder="e.g., (Invited Paper)"
              />
            </div>
            <div className="input-group">
              <label htmlFor="funding">Funding / Financial Support</label>
              <input
                type="text"
                id="funding"
                value={formData.funding}
                onChange={(e) => handleInputChange('funding', e.target.value)}
                placeholder="Identify applicable funding agency here. If none, leave blank."
              />
            </div>
            <div className="input-group checkbox-group">
              <label htmlFor="dropCap" className="checkbox-label">
                <input
                  type="checkbox"
                  id="dropCap"
                  checked={formData.dropCap}
                  onChange={(e) => handleInputChange('dropCap', e.target.checked)}
                />
                Enable Drop Cap on Introduction (First Letter)
              </label>
            </div>
          </div>

          {/* Authors */}
          <div className="form-section">
            <h2>Authors</h2>
            {formData.authors.map((author, index) => (
              <div key={index} className="author-group">
                <h3>Author {index + 1}</h3>
                <div className="author-fields">
                  <div className="input-group">
                    <label>First Name</label>
                    <input
                      type="text"
                      value={author.firstName}
                      onChange={(e) => handleAuthorChange(index, 'firstName', e.target.value)}
                      placeholder="Given Name"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label>Last Name</label>
                    <input
                      type="text"
                      value={author.lastName}
                      onChange={(e) => handleAuthorChange(index, 'lastName', e.target.value)}
                      placeholder="Surname"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label>Membership</label>
                    <input
                      type="text"
                      value={author.membership}
                      onChange={(e) => handleAuthorChange(index, 'membership', e.target.value)}
                      placeholder="e.g., Member, IEEE"
                    />
                  </div>
                  <div className="input-group">
                    <label>Department</label>
                    <input
                      type="text"
                      value={author.department}
                      onChange={(e) => handleAuthorChange(index, 'department', e.target.value)}
                      placeholder="dept. name of organization (of Aff.)"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label>Organization</label>
                    <input
                      type="text"
                      value={author.organization}
                      onChange={(e) => handleAuthorChange(index, 'organization', e.target.value)}
                      placeholder="name of organization (of Aff.)"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label>City, Country</label>
                    <input
                      type="text"
                      value={author.cityCountry}
                      onChange={(e) => handleAuthorChange(index, 'cityCountry', e.target.value)}
                      placeholder="City, Country"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label>Email or ORCID</label>
                    <input
                      type="text"
                      value={author.email}
                      onChange={(e) => handleAuthorChange(index, 'email', e.target.value)}
                      placeholder="email address or ORCID"
                      required
                    />
                  </div>
                </div>
                {formData.authors.length > 1 && (
                  <button type="button" onClick={() => removeAuthor(index)} className="remove-btn">
                    Remove Author
                  </button>
                )}
              </div>
            ))}
            {formData.authors.length < 6 && (
              <button type="button" onClick={addAuthor} className="add-btn">
                Add Another Author
              </button>
            )}
          </div>

          {/* Abstract and Keywords */}
          <div className="form-section">
            <h2>Abstract and Keywords</h2>
            <div className="input-group">
              <label htmlFor="abstract">Abstract</label>
              <textarea
                id="abstract"
                value={formData.abstract}
                onChange={(e) => handleInputChange('abstract', e.target.value)}
                placeholder="This document is a model and instructions for LaTeX..."
                rows="5"
                required
              ></textarea>
              <p className="field-note">CRITICAL: Do Not Use Symbols, Special Characters, Footnotes, or Math in Paper Title or Abstract.</p>
            </div>
            <div className="input-group">
              <label htmlFor="keywords">IEEE Keywords</label>
              <input
                type="text"
                id="keywords"
                value={formData.keywords}
                onChange={(e) => handleInputChange('keywords', e.target.value)}
                placeholder="component, formatting, style, styling, insert"
                required
              />
            </div>
          </div>

          {/* Main Content */}
          <div className="form-section">
            <h2>Main Paper Content</h2>
            {formData.sections.map((section, index) => (
              <div key={index} className="section-group">
                <div className="input-group">
                  <label>{index === 0 ? 'Introduction' : `Section ${toRoman(index + 1)}`}</label>
                  <textarea
                    value={section.content}
                    onChange={(e) => {
                      const updatedSections = [...formData.sections];
                      updatedSections[index].content = e.target.value;
                      setFormData(prev => ({ ...prev, sections: updatedSections }));
                    }}
                    placeholder={`Content for Section ${toRoman(index + 1)}`}
                    rows="6"
                  ></textarea>
                </div>
              </div>
            ))}
            
            <div className="input-group">
              <label htmlFor="references">References</label>
              <textarea
                id="references"
                value={formData.references}
                onChange={(e) => handleInputChange('references', e.target.value)}
                placeholder="\bibitem{b1} G. Eason, B. Noble, and I. N. Sneddon, 'On certain integrals...'"
                rows="6"
              ></textarea>
              <p className="field-note">Please provide bibitems in format: \bibitem&#123;b1&#125; ...</p>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="generate-btn">Generate IEEE PDF</button>
          </div>
        </form>

        {pdfUrl && (
          <div className="download-section">
            <h3>Your IEEE Paper is Ready!</h3>
            <button onClick={downloadPdf} className="download-btn">Download IEEE Conference PDF</button>
          </div>
        )}
      </main>
    </div>

  );
};

// Helper function to convert numbers to Roman numerals
const toRoman = (num) => {
  const romanNumerals = [
    { value: 1000, numeral: 'M' },
    { value: 900, numeral: 'CM' },
    { value: 500, numeral: 'D' },
    { value: 400, numeral: 'CD' },
    { value: 100, numeral: 'C' },
    { value: 90, numeral: 'XC' },
    { value: 50, numeral: 'L' },
    { value: 40, numeral: 'XL' },
    { value: 10, numeral: 'X' },
    { value: 9, numeral: 'IX' },
    { value: 5, numeral: 'V' },
    { value: 4, numeral: 'IV' },
    { value: 1, numeral: 'I' }
  ];

  let result = '';
  for (const { value, numeral } of romanNumerals) {
    while (num >= value) {
      result += numeral;
      num -= value;
    }
  }
  return result;
};

export default App;