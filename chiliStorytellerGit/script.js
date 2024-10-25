fetch("savedSessions.json") 
.then(function(response){
	return response.json();
})
.then(function(sessions){
	let placeholder = document.querySelector("#data-output");
	let out = "";
	for(let session of sessions){
		out += `
			<tr>
				<td>${session.goal}</td>
				<td>${session.when}</td>
				<td>${session.storyContent}</td>
				<td>${session.generatedStory}</td>
                <td>${session.humanGenQuestion}</td>
                <td>${session.AIGenQuestion}</td>
                
			</tr>
		`;
	}
	placeholder.innerHTML = out;
});


