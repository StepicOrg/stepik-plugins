import java.io.BufferedReader;
import java.io.FileReader;

class Main {
    public static void main(String[] args) throws Exception {
        String secretFilePath = "{{ SECRET_FILE }}";
        BufferedReader secretFileReader = new BufferedReader(new FileReader(secretFilePath));
        String secretFileContents = secretFileReader.readLine();
        System.out.println(secretFileContents);
    }
}
