using System.Reflection;

namespace ChattingRoom.Core.Utils;
public static class FileUtils
{
    public static readonly char SPT = Path.DirectorySeparatorChar;
    public static readonly string RootDirectory;
    static FileUtils()
    {
        RootDirectory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)
            ?? throw new Exception("Cannot get root folder.");
    }

    public static string InRootDir(this string fileName)
    {
        return $"{RootDirectory}{SPT}{fileName}";
    }
    public static bool Exists(this string file_dirName)
    {
        return File.Exists(file_dirName) || Directory.Exists(file_dirName);
    }
}
