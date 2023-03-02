using ChatRoom.Core.Interface;
using Newtonsoft.Json.Linq;
using WebSocketSharp;
using WebSocketSharp.Server;

namespace ChatRoom.Server;

public class WebSocketMessageHandlerBehavior : WebSocketBehavior
{
    private ILogger log;

    public WebSocketMessageHandlerBehavior(string name, IServiceProvider sp)
    {
        log = sp.Resolve<ILoggerManager>().OnSubChannel(name);
    }

    protected override void OnMessage(MessageEventArgs e)
    {
        dynamic json = JObject.Parse(e.Data);
        string? messageId = json.MessageID;
        if (messageId is null) return;
    }
}