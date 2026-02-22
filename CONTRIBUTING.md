# Contributing to MediScan AI

Thank you for your interest in contributing! 🎉

## Getting Started

1. **Fork** the repository and clone your fork
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following the guidelines below
4. Run tests: `cd backend && pytest tests/ -v`
5. Open a **Pull Request** against `main`

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add DICOM file support
fix: correct Grad-CAM heatmap normalization
docs: update API reference
test: add coverage for severity triage edge cases
chore: upgrade torch to 2.3.0
```

## Code Style

- **Python**: Black formatter (`black backend/`), max line length 100
- **JavaScript/React**: ESLint + Prettier (`npm run lint`)
- Write docstrings for all public functions
- Add tests for any new feature or bug fix

## PR Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Code formatted (`black .`)
- [ ] No real patient data included
- [ ] HIPAA disclaimer preserved in report output
- [ ] PR description explains the change

## Reporting Issues

Use [GitHub Issues](../../issues). For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## Code of Conduct

Be respectful and inclusive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
