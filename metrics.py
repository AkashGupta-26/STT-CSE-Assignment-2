import shutil
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set

import matplotlib.pyplot as plt

from cfgBuilder import ControlFlowGraph, VariableDefinition, CodeBlock, ControlFlowEdge, CodeStatement


class GraphVisualizationHandler:
    """Handles visualization and output generation for control flow graphs"""
    
    @staticmethod
    def generateDotRepresentation(flowGraph: ControlFlowGraph, outputPath: Path) -> None:
        """Create DOT format representation of the control flow graph"""
        dotLines: List[str] = ["digraph CFG {", "    node [shape=box];"]
        
        # Generate nodes with their statements
        for codeBlock in flowGraph.codeBlocks:
            nodeContentLines = [f"{codeBlock.blockId}:"]
            for statement in codeBlock.codeStatements:
                nodeContentLines.append(statement.content)
            
            escapedContent = "\n".join(nodeContentLines).replace("\"", "\\\"")
            dotLines.append(f"    {codeBlock.blockId} [label=\"{escapedContent}\"];")
        
        # Generate edges between blocks
        for codeBlock in flowGraph.codeBlocks:
            for edge in codeBlock.outgoingEdges:
                if edge.edgeLabel:
                    dotLines.append(f"    {codeBlock.blockId} -> {edge.destinationBlock} [label=\"{edge.edgeLabel}\"];")
                else:
                    dotLines.append(f"    {codeBlock.blockId} -> {edge.destinationBlock};")
        
        dotLines.append("}")
        outputPath.write_text("\n".join(dotLines), encoding="utf-8")

    @staticmethod
    def convertDotToImage(dotFilePath: Path, imageOutputPath: Optional[Path] = None) -> Optional[Path]:
        """Convert DOT file to PNG image using Graphviz"""
        if imageOutputPath is None:
            imageOutputPath = dotFilePath.with_suffix('.png')
        
        graphvizExecutable = shutil.which("dot")
        if not graphvizExecutable:
            print("Graphviz 'dot' executable not found in PATH. Image rendering skipped.")
            return None
        
        try:
            subprocess.run([graphvizExecutable, "-Tpng", str(dotFilePath), "-o", str(imageOutputPath)], check=True)
            return imageOutputPath
        except Exception:
            print(f"Failed to convert {dotFilePath} to PNG format.")
            return None


class DocumentationGenerator:
    """Generates documentation and analysis reports"""
    
    @staticmethod
    def createDefinitionsReport(variableDefinitions: Dict[str, VariableDefinition], outputPath: Path) -> None:
        """Generate markdown table of variable definitions"""
        tableRows: List[str] = [
            "| Definition ID | Variable | Block | Line | Statement |",
            "|---------------|----------|-------|------|-----------|"
        ]
        
        sortedDefinitions = sorted(variableDefinitions.values(), key=lambda def_obj: int(def_obj.defId[1:]))
        for definition in sortedDefinitions:
            escapedStatement = definition.sourceStatement.replace("|", "\\|")
            tableRows.append(f"| {definition.defId} | {definition.variableName} | "
                           f"{definition.containingBlock} | {definition.lineNumber} | `{escapedStatement}` |")
        
        outputPath.write_text("\n".join(tableRows), encoding="utf-8")
    
    @staticmethod
    def formatDefinitionSet(definitionItems: Iterable[str]) -> str:
        """Format a set of definitions for display"""
        if not definitionItems:
            return "{}"
        
        sortedItems = sorted(definitionItems, key=lambda item: (item[0], int(item[1:])))
        return "{" + ", ".join(sortedItems) + "}"
    
    @classmethod
    def generateIterationAnalysis(cls, analysisSnapshots: Sequence[Dict[str, Dict[str, Set[str]]]], 
                                 flowGraph: ControlFlowGraph, outputPath: Path) -> None:
        """Generate detailed iteration-by-iteration analysis report"""
        reportSections: List[str] = []
        
        for iterationIndex, snapshot in enumerate(analysisSnapshots):
            reportSections.append(f"## Iteration {iterationIndex}")
            reportSections.append("| Basic Block | gen[B] | kill[B] | in[B] | out[B] |")
            reportSections.append("|-------------|--------|---------|-------|--------|")
            
            for codeBlock in flowGraph.codeBlocks:
                blockState = snapshot.get(codeBlock.blockId, {})
                reportSections.append("| {blockId} | {gen} | {kill} | {inSet} | {outSet} |".format(
                    blockId=codeBlock.blockId,
                    gen=cls.formatDefinitionSet(blockState.get("gen", set())),
                    kill=cls.formatDefinitionSet(blockState.get("kill", set())),
                    inSet=cls.formatDefinitionSet(blockState.get("in", set())),
                    outSet=cls.formatDefinitionSet(blockState.get("out", set()))
                ))
            
            reportSections.append("")
        
        outputPath.write_text("\n".join(reportSections), encoding="utf-8")