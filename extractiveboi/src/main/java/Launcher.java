import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Launcher {

    public static void main(String[] args) throws FileNotFoundException {
        File dir = new File("../data/");
        File[] files = dir.listFiles();
        for (File story : files) {
            readFile(story);
        }
    }

    private static void readFile(File story) throws FileNotFoundException {
        Scanner scan = new Scanner(story);
        boolean gotHighlights = false;
        boolean prevHighlight = false;
        List<String> sentences = new ArrayList<>();
        while (scan.hasNextLine()) {
            String next = scan.nextLine().trim();
            if (next.equalsIgnoreCase("@highlight")) {
                gotHighlights = true;
                prevHighlight = true;
            } else if (!gotHighlights) {
               
            }
        }
    }

}
