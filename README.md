# Linear Label Action

This is a custom action that adds a label to a Linear issue using the Linear API.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory and add your Linear API key:
```
LINEAR_API_KEY=your_linear_api_key_here
```

You can get your Linear API key from your Linear account settings.

## Usage

You can use this action in three ways:

1. As a module in your code:
```typescript
import { addLinearLabel } from './src/addLinearLabel';

await addLinearLabel({
  labelName: "your-label-name",
  linearId: "your-linear-issue-id",
  linearApiKey: "your-linear-api-key"
});
```

2. From the command line:
```bash
npm run build
node dist/addLinearLabel.js "your-label-name" "your-linear-issue-id"
```

3. As a GitHub Action:
   - Add your Linear API key to your repository's secrets as `LINEAR_API_KEY`
   - The workflow can be triggered in two ways:
     a. Manually through the GitHub Actions UI with custom inputs
     b. Automatically when an issue or PR is labeled

Example workflow usage:
```yaml
# Trigger manually
name: Add Linear Label
on:
  workflow_dispatch:
    inputs:
      label_name:
        description: 'Name of the label to add'
        required: true
      linear_issue_id:
        description: 'Linear Issue ID'
        required: true

# Or trigger automatically on label events
on:
  issues:
    types: [labeled]
  pull_request:
    types: [labeled]
```

Make sure your Linear API key is set in the `.env` file before running the command.

## Building

To build the TypeScript code:
```bash
npm run build
```

## Error Handling

The action will throw an error if:
- The Linear API key is invalid
- The issue ID doesn't exist
- The label name doesn't exist
- There are any API-related issues

Make sure to handle these errors appropriately in your implementation. 