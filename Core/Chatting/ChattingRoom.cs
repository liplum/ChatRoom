using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core;
public class ChattingRoom
{
    private Queue<Action> SchedueledTasks
    {
        get; init;
    } = new();
    private readonly object Lock = new();
    public void AddSchedueledTask(Action task)
    {
        lock (Lock)
        {
            SchedueledTasks.Enqueue(task);
        }
    }

    private void RunSchedueledTasks()
    {
        lock (Lock)
        {
            while (SchedueledTasks.TryDequeue(out var task))
            {
                task();
            }
        }
    }

    public ChattingRoomID ID
    {
        get; set;
    }
}


public struct ChattingRoomID
{
    private readonly int ID;
    public ChattingRoomID(int id)
    {
        ID = id;
    }
    public override bool Equals([NotNullWhen(true)] object? obj)
    {
        return obj is ChattingRoomID o && ID == o.ID;
    }

    public static bool operator ==(ChattingRoomID left, ChattingRoomID right)
    {
        return left.Equals(right);
    }

    public static bool operator !=(ChattingRoomID left, ChattingRoomID right)
    {
        return !(left == right);
    }

    public override int GetHashCode()
    {
        return ID.GetHashCode();
    }
}