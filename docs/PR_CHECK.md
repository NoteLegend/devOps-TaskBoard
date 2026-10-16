# Pull request validation exercise

This isolated documentation change verifies the repository pull-request event. Expected results: PostgreSQL migration/tests, frontend build, both image builds and Trivy scans run; registry login/publishing and AWS deployment are skipped. No deployment credentials should be requested by the PR workflow. The branch is an exercise artifact and does not change the live application.
