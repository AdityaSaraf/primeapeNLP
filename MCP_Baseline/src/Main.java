import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Scanner;
import java.util.Set;

class LabelledDocument {
    public List<String[]> sentences;
    public List<Integer> answers;
    public List<Set<String>> sentenceSets;
    public Set<String> vocabulary;
    public int lengthSummary;

    public LabelledDocument(List<String[]> sentences, List<Integer> answers, List<Set<String>> sentenceSets,
                            Set<String> vocabulary, int lengthSummary) {
        this.sentences = sentences;
        this.answers = answers;
        this.sentenceSets = sentenceSets;
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

        List<LabelledDocument> documents = new ArrayList<>();
        for (File file : files) {
            if (file.isFile()) {
                documents.add(parseFile(file));
            }
        }

        double total = 0;
        for (LabelledDocument document : documents) {
            Set<Integer> generatedSummary = MCPSolver.solve(document.sentenceSets, document.sentences, document.lengthSummary);
            int numCorrect = 0;
            for (int i : document.answers) {
                if (generatedSummary.contains(i)) {
                    numCorrect++;
                }
            }
            double ratioCorrect = (double) numCorrect / document.answers.size();
            total += ratioCorrect;
            System.out.println(ratioCorrect);
            // prints the generated summary
            for (int i : generatedSummary) {
                System.out.println(Arrays.toString(document.sentences.get(i)));
            }
        }
        System.out.println(total/documents.size());

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
        List<String[]> sentences = new ArrayList<>();
        List<Set<String>> sentenceSets = new ArrayList<>();
        Set<String> vocabulary = new HashSet<>();
        List<Integer> answers = new ArrayList<>();
        int lineNum = 0;
        int lengthSummary = 0;
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            if (line.startsWith("2 ")) {
                lengthSummary++;
                continue;
            }
            // TODO: filter sentence based on stopword list
            String[] sentence = line.substring(2).split(" ");
            Set<String> sentenceSet = new HashSet<>(Arrays.asList(sentence));
            filter(sentenceSet);
            sentences.add(sentence);
            sentenceSets.add(sentenceSet);
            vocabulary.addAll(sentenceSet);
            if (line.startsWith("1 ")) {
                answers.add(lineNum);
            }
            lineNum++;
        }
        return new LabelledDocument(sentences, answers, sentenceSets, vocabulary, lengthSummary);
    }

    private static void filter(Set<String> sentenceSet) {
        sentenceSet.removeIf(word -> stopWords.contains(word));
    }

}
