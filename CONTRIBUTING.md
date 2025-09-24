# Contributing to IoTorch

Welcome! We're thrilled you're considering contributing to **IoTorch**, a powerful framework for robust, industrial IoT communications. Whether you're fixing bugs, improving documentation, or proposing new features—your input is valued.

---

## Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Ways to Contribute](#-ways-to-contribute)
- [Getting Started](#-getting-started)
- [Coding Guidelines](#-coding-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Reporting Issues](#-reporting-issues)

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to fostering a welcoming and inclusive environment.

In addition, we require tat all contributors also sign the [Contributor License Agreement](IoTorch_Contributor_License_Agreement.pdf). Please submit the completed agreement to the community moderator (doug@picmg.org)


---

## Ways to Contribute

- Report bugs
- Improve documentation
- Suggest new features
- Submit code fixes or enhancements
- Write tests

---

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/PICMG/IoTorch.git 
## Coding Guidelines
This project creates code for multiple different embedded hardware platforms and developement envioronments. Code for these specific environments is expected to follow the Style Guide for that platform.

When a particular style is not specified for a specific environment, code submitted to this repository should follow the following coding styles:

- **C++** - [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)

- **C** - [GNU Coding Standareds](https://www.gnu.org/prep/standards/)

- **Python** - [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

In addition to following these style guides, all code submissions must include the project's license text within their file header and be free from any confidential or personal information (e.g. login credentials).

## Pull Request Process

Before you begin:

- You need a GitHub account.
- You should have Git installed on your machine.
- Familiarity with basic Git commands is helpful.

---

### 1. Fork the Repository

Go to the main repository on GitHub and click the **Fork** button in the top-right corner. This creates a copy of the repository under your GitHub account.

### 2. Clone Your Fork Locally

Open your terminal and run:

```bash
git clone https://github.com/PICMG/IoTorch.git
cd IoTorch
```



### 3. Create a New Branch

Create a branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

Use a descriptive name like `fix/login-bug` or `feature/add-dark-mode`.

### 4. Make Your Changes

Edit the code, add tests, update documentation—whatever your contribution involves.

### 5. Stage and Commit Your Changes

```bash
git add .
git commit -m "Add: brief description of your change 
signed-off-by: Your-Name <your-email>"
```

Use clear, concise commit messages that explain the "what" and "why" of your changes.  The "signed-off-by" portion of the commit is required for automatic devedeveloper certificate of origin verification.

### 6. Push Your Branch to GitHub

```bash
git push origin feature/your-feature-name
```

### 7. Open a Pull Request

1. Go to your fork on GitHub.
2. Click the **Compare & pull request** button.
3. Fill out the pull request form:
   - Provide a clear title and description.
   - Link any related issues (e.g., `Fixes #12`).
   - Mention any important context or decisions.
4. Submit the pull request.


### 8. Respond to Feedback

A maintainer may review your pull request and suggest changes. Please:

- Be respectful and collaborative.
- Make requested updates promptly.
- Ask questions if anything is unclear.

### 9. Final Checklist

Before submitting your pull request, make sure:

- [ ] Code compiles and passes all tests
- [ ] Changes follow the project’s coding style
- [ ] Documentation is updated (if needed)
- [ ] Your branch is up to date with `main`
- [ ] You’ve run any required linters or formatters
- [ ] If your code is based off of other works (including AI training code) it abides by the license agreements of the original code.

## Reporting Issues
Please check the following before opening a new issue:

- [ ] Search [existing issues](https://github.com/PICMG/IoTorch/issues) to see if your concern has already been reported or addressed.
- [ ] Make sure you're using the latest version of the project.
- [ ] Review the project's `README.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` for guidance.

### How to Submit an Issue
Follow these steps to submit a new issue:

1. Go to the [Issues tab](https://github.com/PICMG/IoTorch/issues) of the repository.
2. Click the **New Issue** button.
3. Choose the appropriate issue template (if available).
4. Fill out the issue form with the following details:

For Bug Reports, make sure you include details for the following items:

- **Description**: What’s happening? What did you expect?
- **Steps to Reproduce**:
- **Environment**:
- **Screenshots or Logs**: If applicable, include images or error messages.

For Feature Requests. please include enough information so that the Community Moderator can understand what is being requested.  In particular, what would you like to see, and Why is it useful or necessary.

For other questions, please be clear and specific and include conext or code snippets if relevant.

After submitting a request, watch for responses from maintainers or other contributors and be ready to clarify or provide additional information.
