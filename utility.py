import argparse
from pathlib import Path
from typing import Dict, List

from readFile import SourceCodeProcessor
from cfgBuilder import constructControlFlowGraph, performReachingDefinitionsAnalysis, detectAmbiguousDefinitions
from metrics import GraphVisualizationHandler, DocumentationGenerator

class ProgramAnalyzer:
    """Handles complete analysis of C programs"""
    
    @staticmethod
    def processProgram(programFilePath: Path, analysisOutputDir: Path) -> Dict[str, int]:
        """Perform complete CFG analysis on a C program"""
        print(f"[info] Processing analysis for {programFilePath.name} ...")
        
        # Load and preprocess source code
        rawSourceCode = SourceCodeProcessor.loadSourceFromFile(str(programFilePath))
        processedSource = SourceCodeProcessor.cleanSourceCode(rawSourceCode)
        mainFunctionBody, startingLineNumber = SourceCodeProcessor.extractMainBody(processedSource)
        
        # Build control flow graph and perform analysis
        controlFlowGraph = constructControlFlowGraph(mainFunctionBody, startingLineNumber)
        reachingDefSnapshots = performReachingDefinitionsAnalysis(controlFlowGraph)
        ambiguousVariables = detectAmbiguousDefinitions(controlFlowGraph)

        # Calculate complexity metrics
        totalNodes = len(controlFlowGraph.codeBlocks)
        totalEdges = sum(len(block.outgoingEdges) for block in controlFlowGraph.codeBlocks)
        cyclomaticComplexityValue = totalEdges - totalNodes + 2

        # Setup output directory
        programIdentifier = programFilePath.stem
        programSpecificOutputDir = analysisOutputDir / programIdentifier
        programSpecificOutputDir.mkdir(parents=True, exist_ok=True)

        # Generate all output files
        cfgDotFilePath = programSpecificOutputDir / "cfg.dot"
        GraphVisualizationHandler.generateDotRepresentation(controlFlowGraph, cfgDotFilePath)
        GraphVisualizationHandler.convertDotToImage(cfgDotFilePath)
        
        DocumentationGenerator.createDefinitionsReport(
            controlFlowGraph.variableDefinitions, 
            programSpecificOutputDir / "definitions.md"
        )
        DocumentationGenerator.generateIterationAnalysis(
            reachingDefSnapshots, 
            controlFlowGraph, 
            programSpecificOutputDir / "reaching_definitions_iterations.md"
        )

        print(f"[completed] {programIdentifier}: Nodes={totalNodes}, Edges={totalEdges}, CC={cyclomaticComplexityValue}")
        return {
            "program": programIdentifier, 
            "nodes": totalNodes, 
            "edges": totalEdges, 
            "cc": cyclomaticComplexityValue
        }

class MetricsReportGenerator:
    """Handles generation of summary reports"""
    
    @staticmethod
    def compileSummaryReport(analysisResults: List[Dict[str, int]], reportOutputDir: Path) -> None:
        """Create a comprehensive metrics summary table"""
        summaryTableRows = [
            "| Program | Nodes (N) | Edges (E) | Cyclomatic Complexity (CC) |",
            "|---------|-----------|-----------|----------------------------|",
        ]
        
        for analysisEntry in analysisResults:
            summaryTableRows.append(
                f"| {analysisEntry['program']} | {analysisEntry['nodes']} | "
                f"{analysisEntry['edges']} | {analysisEntry['cc']} |"
            )
        
        (reportOutputDir / "metrics_summary.md").write_text("\n".join(summaryTableRows), encoding="utf-8")


class CommandLineInterface:
    """Handles command line argument parsing and program execution"""
    
    @staticmethod
    def setupArgumentParser() -> argparse.Namespace:
        """Configure and parse command line arguments"""
        argumentParser = argparse.ArgumentParser(
            description="Execute reaching definitions analysis on C source code files."
        )
        argumentParser.add_argument(
            "sourceFiles",
            type=Path,
            nargs='+',
            help="One or more C source file paths to process (space-separated)."
        )
        argumentParser.add_argument(
            "--analysis-output-dir",
            type=Path,
            default=Path("Output"),
            help="Target directory for analysis output and reports."
        )
        return argumentParser.parse_args()
    
    @classmethod
    def executeAnalysis(cls) -> None:
        """Main execution entry point"""
        commandLineArgs = cls.setupArgumentParser()
        sourceFilePaths: List[Path] = commandLineArgs.sourceFiles
        analysisOutputDirectory: Path = commandLineArgs.analysis_output_dir
        analysisOutputDirectory.mkdir(parents=True, exist_ok=True)

        compiledMetrics: List[Dict[str, int]] = []
        for sourceFile in sourceFilePaths:
            compiledMetrics.append(ProgramAnalyzer.processProgram(sourceFile, analysisOutputDirectory))
        
        MetricsReportGenerator.compileSummaryReport(compiledMetrics, analysisOutputDirectory)


if __name__ == "__main__":
    CommandLineInterface.executeAnalysis()
