import * as vscode from 'vscode';
import axios from 'axios';

let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('vibeguard');
    context.subscriptions.push(diagnosticCollection);

    const scanCommand = vscode.commands.registerCommand('vibeguard.scanFile', async () => {
        await scanCurrentFile();
    });

    context.subscriptions.push(scanCommand);

    // Code Action Provider for Quick Fixes (The lightbulb)
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider('*', new VibeGuardFixProvider(), {
            providedCodeActionKinds: VibeGuardFixProvider.providedCodeActionKinds
        })
    );
}

async function scanCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showInformationMessage('VibeGuard: No active editor found.');
        return;
    }

    const document = editor.document;
    const code = document.getText();
    if (!code.trim()) return;

    // Retrieve settings
    const config = vscode.workspace.getConfiguration('vibeguard');
    const apiUrl = config.get<string>('apiUrl', 'https://vibe-code-security-api.onrender.com');
    const apiKey = config.get<string>('apiKey', '');
    const language = document.languageId;

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "VibeGuard",
        cancellable: false
    }, async (progress) => {
        progress.report({ message: "Analyzing code for vulnerabilities..." });

        try {
            const response = await axios.post(`${apiUrl}/scan`, {
                code: code,
                language: language
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': apiKey
                }
            });

            const results = response.data;
            updateDiagnostics(document, results.issues || []);

            if (results.score === 100) {
                vscode.window.showInformationMessage('VibeGuard: File is secure! (Score: 100)');
            } else {
                vscode.window.showWarningMessage(`VibeGuard: Found ${results.issues.length} vulnerabilities (Score: ${results.score})`);
            }

        } catch (error: any) {
            vscode.window.showErrorMessage(`VibeGuard Scan Failed: ${error.message}`);
        }
    });
}

function updateDiagnostics(document: vscode.TextDocument, issues: any[]) {
    const diagnostics: vscode.Diagnostic[] = [];

    issues.forEach(issue => {
        let lineIdx = 0;
        // Attempt to find the vulnerable snippet location in the document
        if (issue.vulnerable_code_snippet) {
            const lines = document.getText().split('\n');
            const targetLine = issue.vulnerable_code_snippet.split('\n')[0].trim();
            // Find the first line that matches the snippet
            lineIdx = lines.findIndex(l => l.includes(targetLine));
            if (lineIdx === -1) lineIdx = 0; // Fallback to top of file if not precise
        }

        const range = new vscode.Range(lineIdx, 0, lineIdx, document.lineAt(lineIdx).text.length);

        let severity = vscode.DiagnosticSeverity.Warning;
        if (issue.severity?.toUpperCase() === 'CRITICAL' || issue.severity?.toUpperCase() === 'HIGH') {
            severity = vscode.DiagnosticSeverity.Error;
        }

        const diagnostic = new vscode.Diagnostic(range, `VibeGuard: ${issue.description}\n\nHow to fix: ${issue.how_to_fix}`, severity);
        diagnostic.source = 'VibeGuard';

        // Attach the fixed snippet to the diagnostic for the Quick Fix provider
        (diagnostic as any).fixedCode = issue.fixed_code_snippet;

        diagnostics.push(diagnostic);
    });

    diagnosticCollection.set(document.uri, diagnostics);
}

class VibeGuardFixProvider implements vscode.CodeActionProvider {
    public static readonly providedCodeActionKinds = [
        vscode.CodeActionKind.QuickFix
    ];

    public provideCodeActions(document: vscode.TextDocument, range: vscode.Range, context: vscode.CodeActionContext): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        context.diagnostics.filter(diagnostic => diagnostic.source === 'VibeGuard').forEach(diagnostic => {
            const fixedCode = (diagnostic as any).fixedCode;
            if (fixedCode) {
                const action = new vscode.CodeAction('🛡️ VibeGuard: Apply Recommended Fix', vscode.CodeActionKind.QuickFix);
                action.edit = new vscode.WorkspaceEdit();

                // Replace the vulnerable range with the LLM's fixed code
                action.edit.replace(document.uri, diagnostic.range, fixedCode);
                action.diagnostics = [diagnostic];
                action.isPreferred = true;
                actions.push(action);
            }
        });

        return actions;
    }
}

export function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
        diagnosticCollection.dispose();
    }
}
