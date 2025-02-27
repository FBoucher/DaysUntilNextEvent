using System;
using System.Diagnostics.CodeAnalysis;

namespace NextEvent_web.Domain;

public class MySettings
{
    public string ImportantDate { get; set; } = DateTime.Now.ToString("yyyy-MM-dd");
    public string StartFromDay { get; set; } = DateTime.Now.AddDays(-24).ToString("yyyy-MM-dd");

    public string PrimaryRGBColor { get; set; } = string.Empty;

    public string SecondaryRGBColor { get; set; } = string.Empty;

    public bool UseCustomColors { get; set; } = false;
    public string StartTime { get; set; } = "09:00";
    public string EndTime { get; set; } = "22:00";
}
