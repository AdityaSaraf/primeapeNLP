import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MCPSolver {
    public static Set<Integer> solve(List<Set<String>> sentenceSets, List<String[]> sentences, int numSentences) {
        Set<Integer> chosenIndices = new HashSet<>();
        Set<String> chosenWords = new HashSet<>();
        for (int i = 0; i < numSentences; i++) {
            int bestSentence = -1;
            double bestScore = -1;
            for (int j = 0; j < sentenceSets.size(); j++) {
                Set<String> sentenceSet = sentenceSets.get(j);
                double score = 0;
                for (String word : sentenceSet) {
                    if (!chosenWords.contains(word)) {
                        score++;
                    }
                }
                if (score > bestScore) {
                    bestScore = score;
                    bestSentence = j;
                }
            }
            chosenIndices.add(bestSentence);
            chosenWords.addAll(sentenceSets.get(bestSentence));
        }
        return chosenIndices;
    }
}
