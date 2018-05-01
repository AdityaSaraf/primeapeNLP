import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import edu.stanford.nlp.simple.*;
import net.sf.javailp.Linear;
import net.sf.javailp.OptType;
import net.sf.javailp.Problem;
import net.sf.javailp.Result;
import net.sf.javailp.Solver;
import net.sf.javailp.SolverFactory;
import net.sf.javailp.SolverFactoryLpSolve;
import net.sf.javailp.VarType;

public class MCPSolver {
    public static Set<Integer> simpleGreedy(List<String> sentenceStrings, int numSummarySentences) {

        List<Set<String>> sentenceSets = new ArrayList<>(sentenceStrings.size());
        for (int i = 0; i < sentenceStrings.size(); i++) {
            String sentenceStr = sentenceStrings.get(i);
//            Sentence sentence = new Sentence(sentenceStr);
//            Set<String> sentenceSet = new HashSet<>(sentence.lemmas());
            String[] words = sentenceStr.split(" ");
            Set<String> sentenceSet = new HashSet<>(Arrays.asList(words));
            sentenceSets.add(sentenceSet);
        }

        Set<Integer> chosenIndices = new HashSet<>();
        Set<String> chosenWords = new HashSet<>();
        for (int i = 0; i < numSummarySentences; i++) {
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

//    public static Set<Integer> unweightedILP(List<Set<String>> sentenceSets, /*List<String> sentenceStrings,*/
//                                             int numSummarySentences) {
//        Set<String> vocabulary = new HashSet<>();
//        //        List<Set<String>> sentenceSets = new ArrayList<>(sentenceStrings.size());
//        Map<String, Set<Integer>> wordToSentIdx = new HashMap<>();
//        for (int i = 0; i < sentenceSets.size(); i++) {
//            Set<String> sentenceSet = sentenceSets.get(i);
//            //            String sentenceStr = sentenceStrings.get(i);
//            //            Sentence sentence = new Sentence(sentenceStr);
//            //            Set<String> sentenceSet = new HashSet<>(sentence.lemmas());
//            ////            System.out.println(sentenceSet);
//            //            sentenceSets.add(sentenceSet);
//            for (String word : sentenceSet) {
//                Set<Integer> set;
//                if ((set = wordToSentIdx.get(word)) == null) {
//                    set = new HashSet<>();
//                    set.add(i);
//                    wordToSentIdx.put(word, set);
//                }
//                else {
//                    set.add(i);
//                }
//            }
//            vocabulary.addAll(sentenceSet);
//        }

    public static Set<Integer> unweightedILP(List<String> sentenceStrings,
                                             int numSummarySentences) {
        Set<String> vocabulary = new HashSet<>();
        List<Set<String>> sentenceSets = new ArrayList<>(sentenceStrings.size());
        Map<String, Set<Integer>> wordToSentIdx = new HashMap<>();
        for (int i = 0; i < sentenceStrings.size(); i++) {
            String sentenceStr = sentenceStrings.get(i);
            String[] words = sentenceStr.split(" ");
            Set<String> sentenceSet = new HashSet<>(Arrays.asList(words));
//            Sentence sentence = new Sentence(sentenceStr);
//            Set<String> sentenceSet = new HashSet<>(sentence.lemmas());
            sentenceSets.add(sentenceSet);
            for (String word : sentenceSet) {
                Set<Integer> set;
                if ((set = wordToSentIdx.get(word)) == null) {
                    set = new HashSet<>();
                    set.add(i);
                    wordToSentIdx.put(word, set);
                }
                else {
                    set.add(i);
                }
            }
            vocabulary.addAll(sentenceSet);
        }
//        Map<Integer, String> dictionary = new HashMap<>();
//        Map<String, Integer> reverseDictionary = new HashMap<>();
//        int i = 0;
//        for (String word : vocabulary) {
//            dictionary.put(i, word);
//            reverseDictionary.put(word, i);
//            i++;
//        }
        SolverFactory factory = new SolverFactoryLpSolve();
        Problem problem = new Problem();
        // the OPT function is the sum of all words
        Linear optFunction = new Linear();
        // these constraints ensure that each word that's counted in OPT comes
        // from some chosen set
        Linear wordConstraints = new Linear();
        for (String word : vocabulary) {
            optFunction.add(1, word);
            for (Integer idx : wordToSentIdx.get(word)) {
                wordConstraints.add(1, idx);
            }
            wordConstraints.add(-1, word);
            problem.add(wordConstraints, ">=", 0);
            wordConstraints = new Linear();
        }
        problem.setObjective(optFunction, OptType.MAX);
        // this constraint ensures that we choose at most k sets,
        // where k = numSummarySentences
        Linear setConstraints = new Linear();
        for (Integer i = 0; i < sentenceSets.size(); i++) {
            setConstraints.add(1, i);
        }
        problem.add(setConstraints, "<=", numSummarySentences);
        for (Object variable : problem.getVariables()) {
            problem.setVarType(variable, VarType.BOOL);
        }
        Solver solver = factory.get();
        solver.setParameter(Solver.VERBOSE, 0);
        Result result = solver.solve(problem);
//        System.out.println(result);
        Set<Integer> chosenIndices = new HashSet<>();
        for (Integer i = 0; i < sentenceSets.size(); i++) {
            if (result.getBoolean(i)) {
                chosenIndices.add(i);
            }
        }
        return chosenIndices;
    }

//    private static List<Set<String>> makeSetsFromSentStrings(List<String> sentences) {
//
//    }
}
