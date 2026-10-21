# Release Helpdesk walkthrough

An illustrated explanation of the product, architecture, guarded delivery, infrastructure, reconciliation, scaling, monitoring, recovery and cleanup.

- [Editable PowerPoint — 16 slides](Release-Helpdesk-Presentation.pptx)
- [Matching PDF](Release-Helpdesk-Presentation.pdf)
- [Recording guide and speaker notes](Demo-and-Speaker-Notes.md)
- [Engineering review](Project-Review.md)

The deck uses original project screenshots, editable diagrams, clickable evidence and a chart drawn from measured HPA observations. Speaker notes are embedded in PowerPoint and included separately. Allow approximately 12–15 minutes with short screen demonstrations.

Open the PPTX in PowerPoint or LibreOffice Impress, or import it into Google Slides using **File → Import slides → Upload**. Review the imported layout before recording. The PDF is the consistent viewing copy; Noto Sans and DejaVu Sans give the closest local font match.

`build_presentation.py` regenerates the PPTX, PDF, speaker guide and source index using python-pptx, reportlab and Pillow. The PDF comes from the same layout and was visually checked. Native PowerPoint/Google Slides rendering may vary slightly.

The AWS captures show the preserved cloud run before teardown. Fresh source-security and Flux evidence show the later execution on this same application. The final narration should identify those environments clearly.

[Current browser clip](../images/final/browser-walkthrough.webm) records actual local UI operations without narration. Use the speaker guide to cover the complete system in your final recording.
