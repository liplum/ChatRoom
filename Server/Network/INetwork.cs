using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Networks;
public interface INetwork : IInjectable, IMessageChannelContainer
{
    public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token);

    public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null);

    public void StartService();

    public void StopService();
}
