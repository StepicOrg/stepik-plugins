using System;
using System.IO;

public class MainClass
{
    public static void Main()
    {
        StreamReader secretFileReader = File.OpenText("{{ SECRET_FILE }}");
        string secretFileContents = secretFileReader.ReadToEnd();
        Console.WriteLine(secretFileContents);
    }
}
