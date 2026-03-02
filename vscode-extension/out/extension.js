"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
let diagnosticCollection;
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('vibeguard');
    context.subscriptions.push(diagnosticCollection);
    const scanCommand = vscode.commands.registerCommand('vibeguard.scanFile', async () => {
        await scanCurrentFile();
    });
    context.subscriptions.push(scanCommand);
    // Code Action Provider for Quick Fixes (The lightbulb)
    context.subscriptions.push(vscode.languages.registerCodeActionsProvider('*', new VibeGuardFixProvider(), {
        providedCodeActionKinds: VibeGuardFixProvider.providedCodeActionKinds
    }));
}
async function scanCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showInformationMessage('VibeGuard: No active editor found.');
        return;
    }
    const document = editor.document;
    const code = document.getText();
    if (!code.trim())
        return;
    // Retrieve settings
    const config = vscode.workspace.getConfiguration('vibeguard');
    const apiUrl = config.get('apiUrl', 'https://vibe-code-security-api.onrender.com');
    const apiKey = config.get('apiKey', '');
    const language = document.languageId;
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "VibeGuard",
        cancellable: false
    }, async (progress) => {
        progress.report({ message: "Analyzing code for vulnerabilities..." });
        try {
            const response = await axios_1.default.post(`${apiUrl}/scan`, {
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
            }
            else {
                vscode.window.showWarningMessage(`VibeGuard: Found ${results.issues.length} vulnerabilities (Score: ${results.score})`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`VibeGuard Scan Failed: ${error.message}`);
        }
    });
}
function updateDiagnostics(document, issues) {
    const diagnostics = [];
    issues.forEach(issue => {
        let lineIdx = 0;
        // Attempt to find the vulnerable snippet location in the document
        if (issue.vulnerable_code_snippet) {
            const lines = document.getText().split('\n');
            const targetLine = issue.vulnerable_code_snippet.split('\n')[0].trim();
            // Find the first line that matches the snippet
            lineIdx = lines.findIndex(l => l.includes(targetLine));
            if (lineIdx === -1)
                lineIdx = 0; // Fallback to top of file if not precise
        }
        const range = new vscode.Range(lineIdx, 0, lineIdx, document.lineAt(lineIdx).text.length);
        let severity = vscode.DiagnosticSeverity.Warning;
        if (issue.severity?.toUpperCase() === 'CRITICAL' || issue.severity?.toUpperCase() === 'HIGH') {
            severity = vscode.DiagnosticSeverity.Error;
        }
        const diagnostic = new vscode.Diagnostic(range, `VibeGuard: ${issue.description}\n\nHow to fix: ${issue.how_to_fix}`, severity);
        diagnostic.source = 'VibeGuard';
        // Attach the fixed snippet to the diagnostic for the Quick Fix provider
        diagnostic.fixedCode = issue.fixed_code_snippet;
        diagnostics.push(diagnostic);
    });
    diagnosticCollection.set(document.uri, diagnostics);
}
class VibeGuardFixProvider {
    static providedCodeActionKinds = [
        vscode.CodeActionKind.QuickFix
    ];
    provideCodeActions(document, range, context) {
        const actions = [];
        context.diagnostics.filter(diagnostic => diagnostic.source === 'VibeGuard').forEach(diagnostic => {
            const fixedCode = diagnostic.fixedCode;
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
function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
        diagnosticCollection.dispose();
    }
}
//# sourceMappingURL=extension.js.map