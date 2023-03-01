using System.Reflection;

namespace ChatRoom.Core.Util;

public static class FileUtils
{
    public static readonly char Spt = Path.DirectorySeparatorChar;
    public static readonly string RootDirectory;

    static FileUtils()
    {
        RootDirectory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)
                        ?? throw new("Cannot get root folder.");
    }

    public static string InRootDir(this string fileName)
    {
        return $"{RootDirectory}{Spt}{fileName}";
    }

    public static bool Exists(this string fileDirName)
    {
        return File.Exists(fileDirName) || Directory.Exists(fileDirName);
    }
}