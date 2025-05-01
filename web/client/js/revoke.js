function revoke(event_id) {
  axios({
    method: 'delete',
    url: `/query/history/delete/${event_id}`
  })
    .then(result => {
      console.log(result)
      popupTop.innerHTML = '撤销成功！'
      popup.classList.remove('hide')
    })
    .catch(error => {
      console.dir(error)
    })
}
