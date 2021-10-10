namespace ChattingRoom.Server;
public class ChatingRoom
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
}
