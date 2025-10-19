import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class VariableDefinition:
    """Represents a variable definition in the program"""
    defId: str
    variableName: str
    sourceStatement: str
    lineNumber: int
    containingBlock: Optional[str]


@dataclass
class CodeStatement:
    """Represents a single statement in a basic block"""
    content: str
    lineNumber: int
    statementType: str
    associatedDefs: List[str] = field(default_factory=list)


@dataclass
class ControlFlowEdge:
    """Represents an edge between basic blocks in the CFG"""
    destinationBlock: str
    edgeLabel: Optional[str] = None


@dataclass
class CodeBlock:
    """Represents a basic block in the control flow graph"""
    blockId: str
    codeStatements: List[CodeStatement] = field(default_factory=list)
    outgoingEdges: List[ControlFlowEdge] = field(default_factory=list)
    incomingBlocks: Set[str] = field(default_factory=set)
    generatedDefs: List[str] = field(default_factory=list)
    killedDefs: Set[str] = field(default_factory=set)
    reachingIn: Set[str] = field(default_factory=set)
    reachingOut: Set[str] = field(default_factory=set)
    allowAppending: bool = True
    isTerminated: bool = False

    def __hash__(self) -> int:
        return hash(self.blockId)

    def appendStatement(self, statement: CodeStatement) -> None:
        """Add a new statement to this block"""
        self.codeStatements.append(statement)

    def connectToBlock(self, targetBlock: "CodeBlock", connectionLabel: Optional[str] = None) -> None:
        """Create an edge from this block to another block"""
        self.outgoingEdges.append(ControlFlowEdge(targetBlock.blockId, connectionLabel))
        targetBlock.incomingBlocks.add(self.blockId)
        self.allowAppending = False

@dataclass
class ControlFlowGraph:
    """Represents a complete control flow graph with all blocks and definitions"""
    codeBlocks: List[CodeBlock]
    variableDefinitions: Dict[str, VariableDefinition]
    startingBlockId: str
    terminatingBlockIds: Set[str]

    @property
    def blockLookup(self) -> Dict[str, CodeBlock]:
        """Create a mapping from block IDs to block objects"""
        return {block.blockId: block for block in self.codeBlocks}


class FlowGraphConstructor:
    """Builds control flow graphs from source code"""
    
    CONDITIONAL_PATTERNS = re.compile(r'^\s*(if|else\s*if|else|while|for)\b')
    JUMP_PATTERNS = re.compile(r'^\s*(return|break|continue|goto)\b')

    def __init__(self) -> None:
        self.blockIdCounter = 0
        self.definitionIdCounter = 0
        self.constructedBlocks: List[CodeBlock] = []
        self.recordedDefinitions: Dict[str, VariableDefinition] = {}
        self.variableToDefinitions: Dict[str, Set[str]] = {}

    def constructGraphFromSource(self, sourceBody: str, initialLine: int = 1) -> ControlFlowGraph:
        """Build a complete CFG from source code using leader-based approach"""
        processedLines = self.processSourceIntoLines(sourceBody, initialLine)
        
        if not processedLines:
            emptyBlock = self.createNewBlock()
            graph = ControlFlowGraph(self.constructedBlocks, self.recordedDefinitions, 
                                   emptyBlock.blockId, {emptyBlock.blockId})
            self.calculateGenKillSets()
            return graph
        
        leaderPositions = self.identifyLeaderLines(processedLines)
        blockMetadata = self.partitionIntoBlocks(processedLines, leaderPositions)
        blockMapping = self.materializeBlocks(blockMetadata)
        self.establishBlockConnections(blockMapping, processedLines, blockMetadata)
        
        entryBlockId = blockMetadata[0][0]
        exitBlockIds = {block.blockId for block in self.constructedBlocks if not block.isTerminated}
        
        self.calculateGenKillSets()
        return ControlFlowGraph(self.constructedBlocks, self.recordedDefinitions, entryBlockId, exitBlockIds)

    def processSourceIntoLines(self, sourceText: str, initialLineNum: int) -> List[Tuple[str, int]]:
        """Convert source text into list of meaningful statements with line numbers"""
        processedLines, currentLineNum = [], initialLineNum
        for rawLine in sourceText.splitlines():
            cleanedLine = rawLine.strip()
            if cleanedLine and cleanedLine not in {'{', '}', ';'}:
                processedLines.append((cleanedLine, currentLineNum))
            currentLineNum += 1
        return processedLines

    def isConditionalStatement(self, statement: str) -> bool:
        """Check if statement is a conditional control structure"""
        return bool(self.CONDITIONAL_PATTERNS.match(statement))

    def isJumpStatement(self, statement: str) -> bool:
        """Check if statement is a jump/control transfer statement"""
        return bool(self.JUMP_PATTERNS.match(statement))

    def identifyLeaderLines(self, statementList: List[Tuple[str, int]]) -> List[int]:
        """Find leader positions for basic block boundaries"""
        leaderSet = {0} if statementList else set()
        totalStatements = len(statementList)
        
        for index, (statementText, _) in enumerate(statementList):
            if self.isConditionalStatement(statementText):
                leaderSet.update({index, index + 1})
            if self.isJumpStatement(statementText) and index + 1 < totalStatements:
                leaderSet.add(index + 1)
            if statementText.startswith('else'):
                leaderSet.add(index)
        
        return sorted(leaderSet)

    def partitionIntoBlocks(self, statementList: List[Tuple[str, int]], 
                           leaderIndices: List[int]) -> List[Tuple[str, int, List[Tuple[str, int]]]]:
        """Partition statements into basic blocks based on leader positions"""
        if not leaderIndices:
            return []
        
        blockPartitions = []
        for blockIndex, startPos in enumerate(sorted(leaderIndices)):
            endPos = leaderIndices[blockIndex + 1] if blockIndex + 1 < len(leaderIndices) else len(statementList)
            blockPartitions.append((f"B{blockIndex}", startPos, statementList[startPos:endPos]))
        
        return blockPartitions

    def materializeBlocks(self, blockMetadata: List[Tuple[str, int, List[Tuple[str, int]]]]) -> Dict[str, CodeBlock]:
        """Create actual block objects from metadata"""
        blockRegistry = {}
        self.constructedBlocks = []
        
        for blockName, _, statementSlice in blockMetadata:
            newBlock = self.createNewBlock()
            newBlock.blockId = blockName
            blockRegistry[blockName] = newBlock
            
            for statementText, lineNum in statementSlice:
                definitionIds = self.captureDefinitions(statementText, lineNum, newBlock.blockId)
                newBlock.appendStatement(CodeStatement(content=statementText, lineNumber=lineNum, 
                                                     statementType="Stmt", associatedDefs=definitionIds))
        
        self.constructedBlocks = [blockRegistry[f"B{i}"] for i in range(len(blockMetadata))]
        return blockRegistry

    def establishBlockConnections(self, blockRegistry: Dict[str, CodeBlock], lines, blockMetadata) -> None:
        """Create edges between basic blocks based on control flow"""
        connectionList = self.determineControlFlowEdges(lines, blockMetadata)
        for sourceBlock, targetBlock, edgeLabel in connectionList:
            blockRegistry[sourceBlock].connectToBlock(blockRegistry[targetBlock], edgeLabel or None)

    def determineControlFlowEdges(self, lines: List[Tuple[str, int]], 
                                 blockMetadata: List[Tuple[str, int, List[Tuple[str, int]]]]) -> List[Tuple[str, str, str]]:
        """Determine control flow edges between blocks"""
        edgeList, processedEdges = [], set()
        
        for blockIndex, (blockName, _, blockStatements) in enumerate(blockMetadata):
            if not blockStatements:
                if blockIndex + 1 < len(blockMetadata):
                    edgeList.append((blockName, f"B{blockIndex+1}", ""))
                continue
            
            firstStatement, lastStatement = blockStatements[0][0], blockStatements[-1][0]
            isConditional, isJump = self.isConditionalStatement(firstStatement), self.isJumpStatement(lastStatement)
            
            if isConditional:
                if blockIndex + 1 < len(blockMetadata): 
                    edgeList.append((blockName, f"B{blockIndex+1}", "true"))
                if blockIndex + 2 < len(blockMetadata): 
                    edgeList.append((blockName, f"B{blockIndex+2}", "false"))
                if firstStatement.startswith(('while', 'for')) and blockIndex + 1 < len(blockMetadata):
                    edgeList.append((f"B{blockIndex+1}", blockName, "back"))
            elif not isJump and blockIndex + 1 < len(blockMetadata):
                edgeList.append((blockName, f"B{blockIndex+1}", ""))
        
        # Remove duplicate edges
        uniqueEdges = []
        for edge in edgeList:
            if edge not in processedEdges:
                uniqueEdges.append(edge)
                processedEdges.add(edge)
        
        return uniqueEdges

    def createNewBlock(self) -> CodeBlock:
        """Create a new basic block with unique identifier"""
        newBlock = CodeBlock(f"B{self.blockIdCounter}")
        self.blockIdCounter += 1
        self.constructedBlocks.append(newBlock)
        return newBlock

    def captureDefinitions(self, statementText: str, lineNumber: int, blockIdentifier: str) -> List[str]:
        """Extract and record variable definitions from a statement"""
        definedVariables = self.parseDefinedVariables(statementText)
        definitionIds = []
        
        for variableName in definedVariables:
            defId = self.generateDefinitionId()
            self.recordedDefinitions[defId] = VariableDefinition(defId, variableName, 
                                                               statementText.strip(), lineNumber, blockIdentifier)
            self.variableToDefinitions.setdefault(variableName, set()).add(defId)
            definitionIds.append(defId)
        
        return definitionIds

    def parseDefinedVariables(self, statementText: str) -> Set[str]:
        """Extract variables that are defined in the given statement"""
        processedStatement = statementText.strip().rstrip(';')
        definedVars = set()
        
        # Handle variable declarations
        declarationMatch = re.match(r"(int|float|double|char|long|short|unsigned|signed)\b(.*)", processedStatement)
        if declarationMatch:
            for declaration in [part.strip() for part in declarationMatch.group(2).split(',')]:
                variableParts = re.split(r"\s|=|\[", declaration.strip())
                if variableParts and variableParts[0]:
                    definedVars.add(variableParts[0].lstrip('*'))
        
        # Handle assignment statements
        assignmentMatch = re.match(r"([A-Za-z_][A-Za-z0-9_\.]*)\s*([+\-*/%&|^]?=)", processedStatement)
        if assignmentMatch:
            definedVars.add(assignmentMatch.group(1))
        
        # Handle increment/decrement operations
        postIncrementMatch = re.match(r"([A-Za-z_][A-Za-z0-9_\.]*)\s*(\+\+|--)$", processedStatement)
        preIncrementMatch = re.match(r"(\+\+|--)\s*([A-Za-z_][A-Za-z0-9_\.]*)$", processedStatement)
        
        if postIncrementMatch:
            definedVars.add(postIncrementMatch.group(1))
        if preIncrementMatch:
            definedVars.add(preIncrementMatch.group(2))
        
        return definedVars

    def generateDefinitionId(self) -> str:
        """Generate unique identifier for variable definitions"""
        self.definitionIdCounter += 1
        return f"D{self.definitionIdCounter}"

    def calculateGenKillSets(self) -> None:
        """Calculate GEN and KILL sets for all blocks"""
        for block in self.constructedBlocks:
            latestDefinitions, generatedDefs = {}, []
            
            for statement in block.codeStatements:
                for defId in statement.associatedDefs:
                    definition = self.recordedDefinitions[defId]
                    previousDef = latestDefinitions.get(definition.variableName)
                    
                    if previousDef in generatedDefs:
                        generatedDefs.remove(previousDef)
                    
                    latestDefinitions[definition.variableName] = defId
                    generatedDefs.append(defId)
            
            block.generatedDefs = generatedDefs
            killedDefs = set()
            
            for variableName, latestDefId in latestDefinitions.items():
                allDefsForVar = self.variableToDefinitions.get(variableName, set())
                killedDefs.update(allDefsForVar - {latestDefId})
            
            block.killedDefs = killedDefs
            block.reachingIn = set()
            block.reachingOut = set(generatedDefs)


def constructControlFlowGraph(sourceBody: str, initialLine: int = 1) -> ControlFlowGraph:
    """Main entry point for building a CFG from source code"""
    return FlowGraphConstructor().constructGraphFromSource(sourceBody, initialLine)


def performReachingDefinitionsAnalysis(graph: ControlFlowGraph, 
                                     maxIterations: int = 100) -> List[Dict[str, Dict[str, Set[str]]]]:
    """Compute reaching definitions using iterative dataflow analysis"""
    analysisSnapshots = []
    
    # Initialize first snapshot
    initialSnapshot = {}
    for block in graph.codeBlocks:
        initialSnapshot[block.blockId] = {
            "gen": set(block.generatedDefs),
            "kill": set(block.killedDefs),
            "in": set(block.reachingIn),
            "out": set(block.reachingOut)
        }
    analysisSnapshots.append(initialSnapshot)
    
    iterationCount, hasChanges = 0, True
    
    while hasChanges and iterationCount < maxIterations:
        iterationCount += 1
        hasChanges = False
        currentSnapshot = {}
        
        for block in graph.codeBlocks:
            # Compute IN set as union of OUT sets of predecessors
            newInSet = set()
            for predecessorId in block.incomingBlocks:
                predecessorBlock = graph.blockLookup[predecessorId]
                newInSet.update(predecessorBlock.reachingOut)
            
            # Compute OUT set: OUT[B] = GEN[B] ∪ (IN[B] - KILL[B])
            newOutSet = set(block.generatedDefs) | (newInSet - block.killedDefs)
            
            # Check for changes
            if newInSet != block.reachingIn or newOutSet != block.reachingOut:
                block.reachingIn, block.reachingOut = newInSet, newOutSet
                hasChanges = True
            
            currentSnapshot[block.blockId] = {
                "gen": set(block.generatedDefs),
                "kill": set(block.killedDefs),
                "in": set(block.reachingIn),
                "out": set(block.reachingOut)
            }
        
        analysisSnapshots.append(currentSnapshot)
    
    return analysisSnapshots


def detectAmbiguousDefinitions(graph: ControlFlowGraph) -> Dict[str, Dict[str, Set[str]]]:
    """Find variables with multiple reaching definitions (ambiguous variables)"""
    ambiguousResults = {}
    
    for block in graph.codeBlocks:
        variableDefinitionMap = {}
        
        for definitionId in block.reachingIn:
            definition = graph.variableDefinitions[definitionId]
            variableDefinitionMap.setdefault(definition.variableName, set()).add(definitionId)
        
        # Identify variables with multiple definitions
        ambiguousVariables = {var: defs for var, defs in variableDefinitionMap.items() if len(defs) > 1}
        
        if ambiguousVariables:
            ambiguousResults[block.blockId] = ambiguousVariables
    
    return ambiguousResults