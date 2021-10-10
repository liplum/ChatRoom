namespace ChattingRoom.Server.Protocols;
public static class Protocol
{
    public static class StateCode
    {
        public const byte Normal =
            0b_00_00_00_01;
        public const byte Terminal =
            0b_00_00_00_11;
    }

    public const string Datapack = @"
        {
           ""sender"":""192.168.0.1"",
           ""command"":""mssage"",
           ""para"": ""xxxxxxx""
        }";
    public const string DatapackFromServer = @"
        {
           ""sender"":""server"",
           ""command"":""terminal"",
           ""para"":""""
        }";
}
