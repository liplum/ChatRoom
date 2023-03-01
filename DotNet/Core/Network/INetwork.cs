namespace ChattingRoom.Core.Networks;
public interface INetwork : IInjectable, IMessageChannelContainer {

    public delegate void OnClientConnectedHandler([NotNull] NetworkToken token);

    public delegate void OnClientDisconnectedHandler([NotNull] NetworkToken token);

    public delegate void OnMessagePreAnalyzeHandler([AllowNull] NetworkToken token, [NotNull] string sourceText, [NotNull] dynamic json);

    public IEnumerable<NetworkToken> AllConnectedClient {
        get;
    }
    public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token);

    public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null);

    public void StartService();

    public void StopService();

    public bool IsConnected([NotNull] NetworkToken token);

    public event OnClientConnectedHandler OnClientConnected;

    public event OnClientDisconnectedHandler OnClientDisconnected;

    public event OnMessagePreAnalyzeHandler OnMessagePreAnalyze;
}