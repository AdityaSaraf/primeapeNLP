import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FilenameFilter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Scanner;

public class Main {

    // first model is neural, second combinatorial
    static final String firstModel_path = "error_analysis/attn_rnn10";
    static final String secondModel_path = "sample_extracted_mcp_summs";
    static final String firstModelDataPath = "sample_10k_tok";
    static final String secondModelDataPath = "extracted_10k";
    public static void main(String[] args) throws FileNotFoundException {
        FilenameFilter storyFilter = (dir, name) -> {
            String lowercaseName = name.toLowerCase();
            return lowercaseName.endsWith(".story");
        };
        File firstModel_dir = new File(firstModel_path);
        File secondModel_dir = new File(secondModel_path);
        File secondModelDataDir = new File(secondModelDataPath);
        File firstModelDataDir = new File(firstModelDataPath);
        File[] firstModel_files = firstModel_dir.listFiles(storyFilter);
        System.out.println(firstModel_files.length);
        File[] secondModel_files = secondModel_dir.listFiles(storyFilter);
        System.out.println(secondModel_files.length);
        for (int i = 0; i < firstModel_files.length; i++) {
            File firstModel = firstModel_files[i];
            List<String> first_summ = parseFile(firstModel);
            String name = firstModel.getName();
            Object[] rets = getSumms(new File(secondModelDataDir, name));
            List<String> absSum = (List<String>) rets[0];
            HashSet<String> extSum2 = (HashSet<String>) rets[1];
            List<String> origSum = (List<String>) rets[2];
            File secondModel = new File(secondModel_dir, name);
            List<String> second_summ = parseFile(secondModel);
            HashSet<String> extSum1 = (HashSet<String>) getSumms(new File(firstModelDataDir, name))[1];

            int firstCorrect = numCorrect(first_summ, extSum1);
            int secondCorrect = numCorrect(second_summ, extSum2);
            
            if (Math.abs(firstCorrect - secondCorrect) >= 2) {
                System.out.println("-----------------------\nIteration: " + i + ", Extractive Summary for File :" + name);
                for (String sentence : origSum) {
                    System.out.println(sentence);
                }
                System.out.println("\nAbstractive Summary:");
                for (String sentence : absSum) {
                    System.out.println(sentence);
                }
                System.out.println("-----------------------\nFirst Model with " + firstCorrect + " correct:");
                for (String sentence : first_summ) {
                    System.out.println(sentence);
                }
                System.out.println("-----------------------\nSecond Model with " + secondCorrect + " correct:");
                for (String sentence : second_summ) {
                    System.out.println(sentence);
                }
                System.out.println("\n\n");

            }
        }
    }

    private static int numCorrect(List<String> genSum, HashSet<String> extSum) {
        int n = 0;
        for (int i = 0; i < genSum.size(); i++) {
            if (extSum.contains(genSum.get(i).replaceAll(" ", ""))) {
                n++;
            }
        }
        return n;
    }

    private static List<String> parseFile(File file) throws FileNotFoundException {
        FileReader reader = new FileReader(file);
        Scanner scanner =  new Scanner(reader);
        List<String> sentences = new ArrayList<>();
        while (scanner.hasNextLine()) {
            sentences.add(scanner.nextLine());
        }
        return sentences;
    }

    private static Object[] getSumms(File file) throws FileNotFoundException {
        List<String> abstractiveSumm = new ArrayList<>();
        HashSet<String> extractiveSumm = new HashSet<>();
        List<String> originalExt = new ArrayList<>();
        FileReader reader = new FileReader(file);
        Scanner scanner =  new Scanner(reader);
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            String sentence = line.substring(2);
            String modSentence = sentence.replaceAll(" ", "");
            if (line.startsWith("2 ")) {
                abstractiveSumm.add(sentence);
            }
            else if (line.startsWith("1 ")) {
                extractiveSumm.add(modSentence);
                originalExt.add(sentence);
            }
        }
        return new Object[]{abstractiveSumm, extractiveSumm, originalExt};
    }

}
