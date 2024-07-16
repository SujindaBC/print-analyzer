<script lang="ts">
    import { onMount } from 'svelte';
    import axios from 'axios';
    import io from 'socket.io-client';
  
    let file: File | null = null;
    let progress: number = 0;
    let results: any = null;
    let uploading: boolean = false;
    let socket: any;
  
    let paperSize: string = 'A4';
    const paperSizes: string[] = ['A4'];
  
    onMount(() => {
    socket = io('http://localhost:5000');

    socket.on('connect', () => {
      console.log('Connected to server');
    });

    socket.on('progress', (data: { progress: number }) => {
      progress = data.progress;
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });
  });
  
    async function uploadFile() {
      if (!file) return;
  
      uploading = true;
      progress = 0;
      results = null;
  
      const formData = new FormData();
      formData.append('file', file);
      formData.append('paper_size', paperSize);
  
      try {
        const response = await axios.post('http://localhost:8000/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        results = response.data.results;
      } catch (error) {
        console.error('Error uploading file:', error);
      } finally {
        uploading = false;
      }
    }
  
    function handleFileChange(e: Event) {
      const target = e.target as HTMLInputElement;
      if (target && target.files) {
        file = target.files[0];
      }
    }

    function calculateSummary(results: any) {
    if (!results) return { totalPages: 0, totalPrice: 0 };

    let totalPages = Object.keys(results).length;
    let totalPrice = Object.values(results).reduce((acc: number, curr: any) => acc + curr.price, 0);

    return { totalPages, totalPrice };
  }
  </script>
  
  <style>
    /* Your component styles here */
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
  
    th, td {
      border: 1px solid #ccc;
      padding: 8px;
      text-align: left;
    }
  
    th {
      background-color: #f4f4f4;
    }

    .summary {
    margin-top: 20px;
  }
  </style>
  
  <h1>Print Price Analyzer</h1>
  
  <input type="file" on:change={handleFileChange} />
  
  <select bind:value={paperSize}>
    {#each paperSizes as size}
      <option value={size}>{size}</option>
    {/each}
  </select>
  
  <button on:click={uploadFile} disabled={uploading || !file}>
    {uploading ? 'Analyzing...' : 'Analyze'}
  </button>
  
  {#if results}
  <div>
    <h2>Results</h2>
    <div class="summary">
        <h4>Total Pages: {calculateSummary(results).totalPages}</h4>
        <h4>Total Price: {calculateSummary(results).totalPrice} Bath</h4>
    </div>
    <table>
      <thead>
        <tr>
          <th>Page Number</th>
          <th>Black ink usage</th>
          <th>Color ink usage (%)</th>
          <th>Price (Bath)</th>
        </tr>
      </thead>
      <tbody>
        {#each Object.keys(results) as page}
          <tr>
            <td>{page}</td>
            <td>{results[page]["black_ink_usage"]}%</td>
            <td>{results[page]["color_ink_usage"]}%</td>
            <td>{results[page]["price"]}</td>
          </tr>
        {/each}
        <tr>
            <td colspan="3" style="text-align: right;"><strong>Total:</strong></td>
            <td>{calculateSummary(results).totalPrice} Bath</td>
          </tr>
      </tbody>
    </table>
  </div>
{/if}
  