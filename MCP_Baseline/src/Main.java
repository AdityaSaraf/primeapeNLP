import JRouge.common.RougeSummaryModel;
import JRouge.common.ScoreType;
import JRouge.interfaces.IRougeSummaryModel;
import JRouge.rouge.RougeN;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;

class LabelledDocument {
    public String fileName;
    public List<String> originalSentences;
    public List<Integer> answerNums;
    public List<String> filteredSentences;
    public List<String> abstractiveSentences;
    public Set<String> vocabulary;
    public int lengthSummary;

    public LabelledDocument(String fileName, List<String> originalSentences, List<Integer> answerNums, List<String> filteredSentences,
                            List<String> abstractiveSentences, Set<String> vocabulary, int lengthSummary) {
        this.fileName = fileName;
        this.originalSentences = originalSentences;
        this.answerNums = answerNums;
        this.filteredSentences = filteredSentences;
        this.abstractiveSentences = abstractiveSentences;
        this.vocabulary = vocabulary;
        this.lengthSummary = lengthSummary;
    }
}

public class Main {

    static List<String> stopWords = new ArrayList<>();

    public static void main(String[] args) throws IOException {
        File directory = new File("sample_extracted");
        File[] files = directory.listFiles();

        File stopWordFile = new File("stopwords.txt");
        populateStopWordList(stopWordFile);

        File outputDir = new File("sample_extracted_mcp_summs");
        if (!outputDir.exists()) {
            outputDir.mkdir();
        }

        List<LabelledDocument> documents = new ArrayList<>();
        for (File file : files) {
            if (file.isFile()) {
                documents.add(parseFile(file));
            }
        }

        double total = 0;
        int wc = 0;
        for (LabelledDocument document : documents) {
            Set<Integer> generatedSummary = MCPSolver.simpleGreedy(document.filteredSentences, document.lengthSummary);
//            Set<Integer> generatedSummary = MCPSolver.unweightedILP(document.originalSentences, document.lengthSummary);
            List<String> systemSummary = new ArrayList<>();
            List<String> gsSummary = new ArrayList<>();
            for (Integer i : generatedSummary) {
                systemSummary.add(document.originalSentences.get(i));
                wc += document.originalSentences.get(i).split(" ").length;
            }
            for (int i : document.answerNums) {
                gsSummary.add(document.originalSentences.get(i));
            }
            double rougeScore = test(systemSummary, document.abstractiveSentences);
            total += rougeScore;
            System.out.println(rougeScore);
//             prints the generated summary
            File outputFile = new File(outputDir, document.fileName);
            if (outputFile.exists()) {
                outputFile.delete();
            }
            outputFile.createNewFile();
            PrintWriter writer = new PrintWriter(outputFile);
            for (int i : generatedSummary) {
                String sent = document.originalSentences.get(i);
                System.out.println(sent);
                writer.println(sent);
            }
            writer.flush();
        }
        System.out.println("wc = " + wc);
        System.out.println("Average: " + total/documents.size());

    }

    private static double test(List<String> systemSummary, List<String> goldStandardSummary) {
        //            int numCorrect = 0;
        //            for (int i : document.answerNums) {
        //                if (generatedSummary.contains(i)) {
        //                    numCorrect++;
        //                }
        //            }
        //            double ratioCorrect = (double) numCorrect / document.answerNums.size();
        RougeSummaryModel sysSum = new RougeSummaryModel(null);
        for (String sentence : systemSummary) {
            sysSum.addSentence(sentence);
        }
        RougeSummaryModel gs = new RougeSummaryModel(null);
        for (String sentence : goldStandardSummary) {
            gs.addSentence(sentence);
        }
        Set<IRougeSummaryModel> s = new HashSet<>();
        s.add(gs);
        RougeN rouge = new RougeN(sysSum, s, Integer.MAX_VALUE, Integer.MAX_VALUE, 1, 'A', 0.5);
        Map<ScoreType, Double> results = rouge.computeNGramScore();
        return results.get(ScoreType.F);
    }

    private static void populateStopWordList(File file) throws FileNotFoundException {
        FileReader reader = new FileReader(file);
        Scanner scanner =  new Scanner(reader);
        while (scanner.hasNextLine()) {
            stopWords.add(scanner.nextLine());
        }
    }

    private static LabelledDocument parseFile(File file) throws FileNotFoundException {
        FileReader reader = new FileReader(file);
        Scanner scanner =  new Scanner(reader);
        List<String> filteredSentences = new ArrayList<>();
        Set<String> vocabulary = new HashSet<>();
        List<Integer> answerNums = new ArrayList<>();
        List<String> originalSentences = new ArrayList<>();
        List<String> summarySentences = new ArrayList<>();
        int lineNum = 0;
        int lengthSummary = 0;
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            if (line.startsWith("2 ")) {
                lengthSummary++;
                summarySentences.add(line.substring(2));
                continue;
            }
            String[] sentence = line.substring(2).split(" ");
            StringBuilder sb = new StringBuilder();
            for (String word : sentence) {
                if (!stopWords.contains(word)) {
                    sb.append(word).append(" ");
                    vocabulary.add(word);
                }
            }
            filteredSentences.add(sb.toString());
            originalSentences.add(line.substring(2));
            if (line.startsWith("1 ")) {
                answerNums.add(lineNum);
            }
            lineNum++;
        }
        return new LabelledDocument(file.getName(), originalSentences, answerNums, filteredSentences,
                                    summarySentences, vocabulary, lengthSummary);
    }

    private static void filter(Set<String> sentenceSet) {
        sentenceSet.removeIf(word -> stopWords.contains(word));
    }

}
