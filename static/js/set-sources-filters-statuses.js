function setSourcesFiltersStatuses(data) {
  if (data.status.sourceName === "Camera1" && data.status.filterName === "Cam1replay") {
    if (data.status.filterEnabled) {
      classListRemove('cam1replayButton', 'filter-disabled');
      classListAdd('cam1replayButton', 'filter-enabled');
    } else {
      classListRemove('cam1replayButton', 'filter-enabled');
      classListAdd('cam1replayButton', 'filter-disabled');
    }
  };
  if (data.status.sourceName === "Camera2" && data.status.filterName === "Cam2replay") {
    if (data.status.filterEnabled) {
      classListRemove('cam2replayButton', 'filter-disabled');
      classListAdd('cam2replayButton', 'filter-enabled');
    } else {
      classListRemove('cam2replayButton', 'filter-enabled');
      classListAdd('cam2replayButton', 'filter-disabled');
    }
  }
}