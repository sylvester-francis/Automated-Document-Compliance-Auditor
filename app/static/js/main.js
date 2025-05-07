document.addEventListener('DOMContentLoaded', function() {
    // Highlight paragraphs with issues
    const issueElements = document.querySelectorAll('.compliance-issue');
    issueElements.forEach(issue => {
        issue.addEventListener('mouseenter', function() {
            const paragraphId = this.getAttribute('data-paragraph-id');
            if (paragraphId) {
                const paragraph = document.getElementById('para-' + paragraphId);
                if (paragraph) {
                    paragraph.classList.add('highlight-active');
                }
            }
        });
        
        issue.addEventListener('mouseleave', function() {
            const paragraphId = this.getAttribute('data-paragraph-id');
            if (paragraphId) {
                const paragraph = document.getElementById('para-' + paragraphId);
                if (paragraph) {
                    paragraph.classList.remove('highlight-active');
                }
            }
        });
    });
    
    // Add data attributes to compliance issues for highlighting
    document.querySelectorAll('.compliance-issue').forEach(function(issue) {
        const issueId = issue.id.replace('issue-', '');
        const paragraphId = issue.querySelector('[data-paragraph-id]')?.getAttribute('data-paragraph-id');
        if (paragraphId) {
            issue.setAttribute('data-paragraph-id', paragraphId);
        }
    });
});