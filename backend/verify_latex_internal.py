from app import generate_latex_document

mock_data = {
    "title": "My Awesome Paper",
    "funding": "National Science Foundation",
    "paperNotice": "Invited Paper",
    "dropCap": True,
    "authors": [
        {
            "firstName": "John", "lastName": "Doe", "membership": "Member, IEEE",
            "department": "Dept of CS", "organization": "Univ A",
            "cityCountry": "City, Country", "email": "john@example.com"
        },
        {
            "firstName": "Jane", "lastName": "Smith",
            "department": "Dept of EE", "organization": "Univ B",
            "cityCountry": "City, Country", "email": "jane@example.com"
        }
    ],
    "abstract": "This is the abstract.",
    "keywords": "AI, ML, Testing",
    "sections": [
        {"title": "Introduction", "content": "Hello World this is a drop cap test."},
        {"title": "Methodology", "content": "We did stuff."}
    ],
    "references": "\\bibitem{b1} Ref 1"
}

latex = generate_latex_document(mock_data)
with open('verify_output_internal.tex', 'w') as f:
    f.write(latex)
print("Wrote to verify_output_internal.tex")
