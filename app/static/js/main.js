document.addEventListener('DOMContentLoaded', function() {
    // Highlight paragraphs with issues
    const issueElements = document.querySelectorAll('.compliance-issue');
    issueElements.forEach(issue => {
        // Extract paragraph ID from issue ID
        const issueId = issue.id;
        if (issueId) {
            const paragraphId = issue.getAttribute('data-paragraph-id');
            
            // Handle mouse hover effects
            issue.addEventListener('mouseenter', function() {
                if (paragraphId) {
                    const paragraph = document.getElementById('para-' + paragraphId);
                    if (paragraph) {
                        paragraph.classList.add('highlight-active');
                    }
                }
            });
            
            issue.addEventListener('mouseleave', function() {
                if (paragraphId) {
                    const paragraph = document.getElementById('para-' + paragraphId);
                    if (paragraph) {
                        paragraph.classList.remove('highlight-active');
                    }
                }
            });
        }
    });
    
    // Add data attributes to compliance issues for highlighting
    document.querySelectorAll('.compliance-issue').forEach(function(issue) {
        const issueId = issue.id.replace('issue-', '');
        const paragraphIdElement = issue.querySelector('[data-paragraph-id]');
        
        // For each issue, find the paragraph ID from the issue data
        if (!paragraphIdElement) {
            // Try to extract from results data
            const paragraphId = issue.getAttribute('data-paragraph-id');
            if (!paragraphId) {
                // If attribute not found, try to extract from the id of nearby elements
                const issues = document.querySelectorAll("[id^='issue-']");
                for (let i = 0; i < issues.length; i++) {
                    if (issues[i].id === issue.id) {
                        // Found the matching issue, now get the paragraph ID
                        const suggestionButton = issue.querySelector('button[hx-get]');
                        if (suggestionButton) {
                            const hxGet = suggestionButton.getAttribute('hx-get');
                            if (hxGet && hxGet.includes('/suggest/')) {
                                // Extract issue ID from the hx-get URL
                                const parts = hxGet.split('/');
                                const extractedIssueId = parts[parts.length - 1];
                                
                                // Find the paragraph ID from the document data
                                if (window.complianceData && window.complianceData.issues) {
                                    const issueData = window.complianceData.issues.find(i => i.issue_id === extractedIssueId);
                                    if (issueData) {
                                        issue.setAttribute('data-paragraph-id', issueData.paragraph_id);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    });
    
    // Handle suggestion generation status
    const suggestionButtons = document.querySelectorAll('button[hx-get*="/suggest/"]');
    suggestionButtons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Generating suggestion for issue...');
        });
    });
});